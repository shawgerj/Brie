import datetime
from django.utils.timezone import utc
from django.test import TestCase, Client
from tastypie.test import ResourceTestCase
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord, TimeclockAction
from django.contrib.auth.models import User


###
# Model Test Cases
###

class ListservModelTestCase(TestCase):
    def test_listserv(self):
        self.l1 = Listserv.objects.create(email='tech@listserv.it.northwestern.edu')
        
        self.assertEquals(self.l1.email, 'tech@listserv.it.northwestern.edu')

class DisciplineRecordTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']
    def test_disciplinerecord(self):
        self.d1 = DisciplineRecord.objects.create(date_of_record=datetime.datetime.utcnow().replace(tzinfo=utc), employee = User.objects.get(pk=2), changed_by = User.objects.get(pk=3), status_name = 'nd', comment = 'this is a comment')
        
        self.assertEquals(self.d1.employee.username, 'testcon')
        self.assertEquals(self.d1.changed_by.username, 'testcl')

class ShiftTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']
    def test_shift(self):
        time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.s1 = Shift.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), location_name = Location.objects.get(pk='Tech'), worker = User.objects.get(pk=3), for_trade = False, been_traded = False)
        self.s2 = Shift.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), location_name = Location.objects.get(pk='Tech'), worker = User.objects.get(pk=2), for_trade = True, been_traded = True)

        self.assertEquals(self.s1.for_trade, False)
        self.assertEquals(self.s2.for_trade, True)
        self.assertEquals(self.s1.worker.username, 'testcl')
        self.assertEquals(self.s2.worker.username, 'testcon')

class PlannerBlockTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']
    def test_plannerblock(self):
        time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.pb1 = PlannerBlock.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), worker = User.objects.get(pk=3), block_type = 'pf')
        
        self.assertEquals(self.pb1.worker.username, 'testcl')
        self.assertEquals(self.pb1.end_time - self.pb1.start_time, datetime.timedelta(hours=1))
        self.assertEquals(self.pb1.get_block_type_display(), "Preferred")

class TimeclockRecordTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']
    def test_timeclockrecord(self):
        time = datetime.datetime.utcnow().replace(tzinfo=utc)
        loc = Location.objects.get(pk='Tech')
        self.tr1 = TimeclockRecord.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), inIP = loc.ip_address, outIP = loc.ip_address, employee = User.objects.get(pk=3))

        self.assertEquals(self.tr1.employee.username, 'testcl')
        self.assertEquals(self.tr1.end_time - self.tr1.start_time, datetime.timedelta(hours=1))
        self.assertEquals(self.tr1.inIP, self.tr1.outIP)

class TimeclockActionTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']
    def test_timeclockaction(self):
        t = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.ta1 = TimeclockAction.objects.create(time=t, IP = '127.0.0.1', employee = User.objects.get(pk=3))

        self.assertEquals(self.ta1.employee.username, 'testcl')
        self.assertEquals(self.ta1.time, t)
        self.assertEquals(self.ta1.IP, '127.0.0.1')


class LocationModelTestCase(TestCase):
    def test_location(self):
        # note that we are testing against the data in initial.yaml
        # not sure if that is the best behavior or not
        self.assertEquals(Location.objects.count(), 6)

        l1 = Location.objects.get(pk='Tech')
        l2 = Location.objects.get(pk='PC-MAC')

        self.assertEquals(l1.address, '2145 Sheridan Road')
        self.assertNotEquals(l1.address, '1970 Campus Drive')
        self.assertEquals(l2.address, '1970 Campus Drive')

    
###
# Tastypie API Test Cases
###

class LocationResourceTest(ResourceTestCase):
    fixtures = ['ricotta_test_data.json']
    def setUp(self):
        super(LocationResourceTest, self).setUp()

        self.testcl = User.objects.get(pk=1)
        self.testcon = User.objects.get(pk=2)
        
        self.post_data_loc = {
            'location_name': 'NewLoc',
            'ip_address': '123.456.789.012',
            'enable_schedule': True,
            'phone_number': '123-456-7890',
            'address': '1970 Campus Dr.',
        }

    def get_normal_credentials(self):
        return self.create_apikey(username=self.testcon.username, 
                                  api_key=self.testcon.api_key.key)
    def get_admin_credentials(self):
        return self.create_apikey(username=self.testcl.username,
                                  api_key=self.testcl.api_key.key)
        
    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/location/', format='json')
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 6)
        
        # might as well test if user permissions work, although we don't 
        # actually need them
        resp = self.api_client.get('/api/v1/location/', format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)
        resp = self.api_client.get('/api/v1/location/', format='json', authentication=self.get_admin_credentials())
        self.assertValidJSONResponse(resp)

    def test_get_detail_json(self):
        resp = self.api_client.get('/api/v1/location/Tech/', format='json')
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp), 
                        ['location_name', 'ip_address', 'enable_schedule'])

        resp = self.api_client.get('/api/v1/location/Tech/', format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)
        resp = self.api_client.get('/api/v1/location/Tech/', format='json', authentication=self.get_admin_credentials())
        self.assertValidJSONResponse(resp)


    # POST should be illegal here
    def test_post_loc(self):
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/v1/location/', format='json', data=self.post_data_loc))
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/v1/location/', format='json', data=self.post_data_loc, authentication=self.get_normal_credentials()))
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/v1/location/', format='json', data=self.post_data_loc, authentication=self.get_admin_credentials()))
    
    # as should DELETE
    def test_delete_loc(self):
        self.assertHttpMethodNotAllowed(self.api_client.delete('/api/v1/location/Tech/', format='json'))
        self.assertHttpMethodNotAllowed(self.api_client.delete('/api/v1/location/Tech/', format='json', authentication=self.get_normal_credentials()))
        self.assertHttpMethodNotAllowed(self.api_client.delete('/api/v1/location/Tech/', format='json', authentication=self.get_admin_credentials()))
        
        
class ShiftResourceTest(ResourceTestCase):
    fixtures = ['ricotta_test_data.json']

    # note: eventually to make all the permissions right....
    # unauthenticated users should not be able to see any shifts.
    # testcon and testcl should each be able to see each other's shifts
    # testcon should be able to put his shift up for trade, but not testcl's
    # testcon should not be able to delete his shift or change ownership
    # testcl should be able to make any changes to his or testcon's shifts
    def setUp(self):
        super(ShiftResourceTest, self).setUp()

        self.testcl = User.objects.get(pk=3)
        self.testcon = User.objects.get(pk=2)

        self.shift_1 = Shift.objects.get(pk=1)
        self.shift_2 = Shift.objects.get(pk=2)
        self.detail_url_1 = '/api/v1/shift/{0}/' .format(self.shift_1.pk) 
        self.detail_url_2 = '/api/v1/shift/{0}/' .format(self.shift_2.pk) 

        # create a shift
        self.post_data_adm = {
            'start': '2012-07-10T10:00:00',
            'end': '2012-07-10T12:00:00',
            'title': 'testcl',
            'location_name': 'Tech',
            'allDay': False,
            'color': 'Blue',
        }
        self.post_data_nml = {
            'start': '2012-07-10T12:00:00',
            'end': '2012-07-10T14:00:00',
            'title': 'testcon',
            'location_name': 'Tech',
            'allDay': False,
            'color': 'Blue',
        }

    
    def get_normal_credentials(self):
        return self.create_apikey(username=self.testcon.username, 
                                  api_key=self.testcon.api_key.key)
    def get_admin_credentials(self):
        return self.create_apikey(username=self.testcl.username,
                                  api_key=self.testcl.api_key.key)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/shift/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/shift/', format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        resp = self.api_client.get('/api/v1/shift/', format='json', authentication=self.get_admin_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

    def test_get_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url_1, format='json'))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url_1, format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)
        resp = self.api_client.get(self.detail_url_1, format='json', authentication=self.get_admin_credentials())
        self.assertValidJSONResponse(resp)

        # TODO: I think this should be cleaned up. Do we really need id and resource_uri?
        self.assertKeys(self.deserialize(resp),
                        ['start', 'end', 'allDay', 'title', 'id', 'location_name', 'color', 'resource_uri', 'for_trade', 'been_traded'])

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/shift/', format='json', data=self.post_data_nml))

    def test_post_list(self):
        self.assertEqual(Shift.objects.count(), 2)
        # normal users cannot POST a shift (even if it belongs to them)
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/shift/', format='json', data=self.post_data_nml, authentication=self.get_normal_credentials()))
        # but admin users can. Here we create a shift for nml and adm users
        self.assertHttpCreated(self.api_client.post('/api/v1/shift/', format='json', data=self.post_data_nml, authentication=self.get_admin_credentials()))
        self.assertHttpCreated(self.api_client.post('/api/v1/shift/', format='json', data=self.post_data_adm, authentication=self.get_admin_credentials()))

        self.assertEqual(Shift.objects.count(), 4)

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url_1, format='json'))

    def test_delete_detail_normal(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url_1, format='json', authentication=self.get_normal_credentials()))

    def test_delete_detail_admin(self):
        self.assertEqual(Shift.objects.count(), 2)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url_1, format='json', authentication=self.get_admin_credentials()))
        self.assertEqual(Shift.objects.count(), 1)

    def test_testcon_trade(self):
        self.assertEqual(Shift.objects.get(pk=1).for_trade, False)
        original_data = self.deserialize(self.api_client.get(self.detail_url_1, format='json', authentication=self.get_normal_credentials()))
        new_data = original_data.copy()
        new_data['for_trade'] = True
        new_data['been_traded'] = True
        self.assertHttpAccepted(self.api_client.put(self.detail_url_1, format='json', data=new_data, authentication=self.get_normal_credentials()))
        self.assertEqual(Shift.objects.get(pk=1).for_trade, True)
        self.assertEqual(Shift.objects.get(pk=1).been_traded, True)

        # should not be able to do this on somebody else's shift
        self.assertEqual(Shift.objects.get(pk=2).for_trade, False)
        original_data = self.deserialize(self.api_client.get(self.detail_url_2, format='json', authentication=self.get_normal_credentials()))
        new_data = original_data.copy()
        new_data['for_trade'] = True
        new_data['been_traded'] = True
        self.assertHttpAccepted(self.api_client.put(self.detail_url_2, format='json', data=new_data, authentication=self.get_normal_credentials()))        
        self.assertEqual(Shift.objects.get(pk=2).for_trade, False)
        self.assertEqual(Shift.objects.get(pk=2).been_traded, False)
                

    def test_shift_trade(self):
        self.assertEqual(Shift.objects.get(pk=1).for_trade, False)
        original_data = self.deserialize(self.api_client.get(self.detail_url_1, format='json', authentication=self.get_admin_credentials()))
        new_data = original_data.copy()
        new_data['for_trade'] = True
        new_data['been_traded'] = True
        self.assertHttpAccepted(self.api_client.put(self.detail_url_1, format='json', data=new_data, authentication=self.get_admin_credentials()))
        self.assertEqual(Shift.objects.get(pk=1).for_trade, True)
        self.assertEqual(Shift.objects.get(pk=1).been_traded, True)

        self.assertEqual(Shift.objects.get(pk=2).for_trade, False)
        original_data = self.deserialize(self.api_client.get(self.detail_url_2, format='json', authentication=self.get_admin_credentials()))
        new_data = original_data.copy()
        new_data['for_trade'] = True
        new_data['been_traded'] = True
        self.assertHttpAccepted(self.api_client.put(self.detail_url_2, format='json', data=new_data, authentication=self.get_admin_credentials()))        
        self.assertEqual(Shift.objects.get(pk=2).for_trade, True)
        self.assertEqual(Shift.objects.get(pk=2).been_traded, True)

    def test_shift_pickup_trade(self):
        original_data = self.deserialize(self.api_client.get(self.detail_url_2, format='json', authentication=self.get_admin_credentials()))
        new_data = original_data.copy()
        new_data['for_trade'] = True
        new_data['been_traded'] = True
        self.api_client.put(self.detail_url_2, format='json', data=new_data, authentication=self.get_admin_credentials())
        self.assertEqual(Shift.objects.get(pk=2).for_trade, True)
        self.assertEqual(Shift.objects.get(pk=2).worker, User.objects.get(username='testcl'))

        # now that this shift owned by testcl is up for trade, let's try to 
        # take it with testcon
        new_data['title'] = 'testcon'
        new_data['for_trade'] = False
        self.assertHttpAccepted(self.api_client.put(self.detail_url_2, format='json', data=new_data, authentication=self.get_normal_credentials()))
        self.assertEqual(Shift.objects.get(pk=2).for_trade, False)
        self.assertEqual(Shift.objects.get(pk=2).worker, User.objects.get(username='testcon'))

class PlannerBlockResourceTest(ResourceTestCase):
    fixtures = ['ricotta_test_data.json']

    def setUp(self):
        super(PlannerBlockResourceTest, self).setUp()

        self.testcl = User.objects.get(pk=3)
        self.testcon = User.objects.get(pk=2)

        self.pb_1 = PlannerBlock.objects.get(pk=1)
        self.pb_2 = PlannerBlock.objects.get(pk=2)
        self.detail_url_1 = '/api/v1/planner_block/{0}/' .format(self.pb_1.pk)
        self.detail_url_2 = '/api/v1/planner_block/{0}/' .format(self.pb_2.pk)
        
        # some POST data for later
        self.post_data_adm = {
            'start': '2012-07-18T10:00:00',
            'end': '2012-07-18T12:00:00',
            'title': 'pf',
            'allDay': False
        }
        self.post_data_nml = {
            'start': '2012-07-18T11:00:00',
            'end': '2012-07-18T13:00:00',
            'title': 'pf',
            'allDay': False
        }

    def get_normal_credentials(self):
        return self.create_apikey(username=self.testcon.username,
                                  api_key=self.testcon.api_key.key)
    def get_admin_credentials(self):
        return self.create_apikey(username=self.testcl.username,
                                  api_key=self.testcl.api_key.key)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/planner_block/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/planner_block/', format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

        resp = self.api_client.get('/api/v1/planner_block/', format='json', authentication=self.get_admin_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url_1, format='json'))

    def test_get_detail(self):
        resp = self.api_client.get(self.detail_url_1, format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url_1, format='json'))
    
    def test_delete_detail(self):
        # a normal user should be able to delete their own planner block
        self.assertEqual(PlannerBlock.objects.count(), 2)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url_1, format='json', authentication=self.get_normal_credentials()))
        self.assertEqual(PlannerBlock.objects.count(), 1)


        
###
# Views Test Cases
###

class CalendarViewsTestCase(TestCase):
    # again we are using the location info in initial.yaml
    def test_location_indices(self):
        # test all the existing locations
        for l in Location.objects.all():
            resp = self.client.get('/ricotta/calendar/' + l.location_name + '/')
            self.assertEqual(resp.status_code, 200)
            self.assertTrue('location_name' in resp.context)

        # make sure if a location doesn't exist, we return a 404
        resp = self.client.get('/calendar/nonexistantlab/')
        self.assertEqual(resp.status_code, 404)

class PlannerViewsTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']

    def test_planner_detail(self):
        # check to make sure both of these planners exist
        resp = self.client.get('/ricotta/planner/testcl/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)
        resp = self.client.get('/ricotta/planner/testcon/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)

        # and if we try a user that doesn't exist, return 404
        resp = self.client.get('/planner/notusr/')
        self.assertEqual(resp.status_code, 404)

class ClockInTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']

    def setUp(self):
        self.client = Client(HTTP_X_FORWARDED_FOR = '127.0.0.1')
        self.client.login(username='testcon', password='testcon')
    
    # we start with no timeclockactions, so this is a simple clockin
    def test_clockin(self):
        resp = self.client.get('/ricotta/clockin/')
        # need to test for the redirect
        self.assertEqual(resp.status_code, 302)
        ta = TimeclockAction.objects.all()
        
        self.assertEqual(ta.count(), 1)
        self.assertEqual(ta[0].IP, '127.0.0.1')
        self.assertEqual(ta[0].employee.username, 'testcon')
        
        # get rid of this one so it doesn't mess up our clockout test next
        ta[0].delete()
        
    def test_clockout(self):
        t = datetime.datetime.utcnow().replace(tzinfo=utc)
        user = User.objects.get(pk=2)
        # create a clock-in record so we can clock out two hours later
        ta_in = TimeclockAction(employee=user, 
                                IP='127.0.0.1',
                                time=(t - datetime.timedelta(hours=2))).save()
        
        resp = self.client.get('/ricotta/clockin/')
        self.assertEqual(resp.status_code, 302)
        ta = TimeclockAction.objects.all()
        
        # the one we created above should have been removed.
        self.assertEqual(ta.count(), 0)
        
        tr = TimeclockRecord.objects.all()
        # and we should have two timeclock records 
        # (one from the fixture and one just created)
        self.assertEqual(tr.count(), 2)
        tr_2 = TimeclockRecord.objects.get(pk=2)
        self.assertEqual(tr_2.employee.username, 'testcon')
        # just test for 7200 seconds (2 hours). There are some microseconds
        # we don't need to worry about
        self.assertEqual((tr_2.end_time - tr_2.start_time).seconds, 7200)
                                               
                                               
