import datetime
from django.utils.timezone import utc
from django.test import TestCase
from tastypie.test import ResourceTestCase
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord
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
        self.detail_url = '/api/v1/shift/{0}/' .format(self.shift_1.pk)

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
        resp = self.api_client.get('/api/v1/shift/', format='json', authentication=self.get_admin_credentials())
        self.assertValidJSONResponse(resp)


        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        
    def test_get_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_normal_credentials())
        self.assertValidJSONResponse(resp)
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_admin_credentials())
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
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json'))
                

###
# Views Test Cases
###

class CalendarViewsTestCase(TestCase):
    # again we are using the location info in initial.yaml
    def test_location_indices(self):
        # test all the existing locations
        for l in Location.objects.all():
            resp = self.client.get('/calendar/' + l.location_name + '/')
            self.assertEqual(resp.status_code, 200)
            self.assertTrue('location_name' in resp.context)

        # make sure if a location doesn't exist, we return a 404
        resp = self.client.get('/calendar/nonexistantlab/')
        self.assertEqual(resp.status_code, 404)

class PlannerViewsTestCase(TestCase):
    fixtures = ['ricotta_test_data.json']

    def test_planner_detail(self):
        # check to make sure both of these planners exist
        resp = self.client.get('/planner/testcl/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)
        resp = self.client.get('/planner/testcon/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)

        # and if we try a user that doesn't exist, return 404
        resp = self.client.get('/planner/notusr/')
        self.assertEqual(resp.status_code, 404)
