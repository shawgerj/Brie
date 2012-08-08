import datetime
from tastypie.test import ResourceTestCase
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord, TimeclockAction
from django.contrib.auth.models import User
from ricotta.tests.factories import *

class LocationResourceTest(ResourceTestCase):
    def setUp(self):
        super(LocationResourceTest, self).setUp()

        self.testcl = ConleaderFactory.create().user
        self.testcon = ConsultantFactory.create().user
        
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
    # note: eventually to make all the permissions right....
    # unauthenticated users should not be able to see any shifts.
    # testcon and testcl should each be able to see each other's shifts
    # testcon should be able to put his shift up for trade, but not testcl's
    # testcon should not be able to delete his shift or change ownership
    # testcl should be able to make any changes to his or testcon's shifts
    def setUp(self):
        super(ShiftResourceTest, self).setUp()

        self.testcl = ConleaderFactory.create().user
        self.testcon = ConsultantFactory.create().user
        self.loc = Location.objects.get(location_name="Tech")

        self.shift_1 = ShiftFactory.create(worker=self.testcon, 
                                           location_name=self.loc)
        self.shift_2 = ShiftFactory.create(worker=self.testcl, 
                                           location_name=self.loc)
        self.detail_url_1 = '/api/v1/shift/{0}/' .format(self.shift_1.pk) 
        self.detail_url_2 = '/api/v1/shift/{0}/' .format(self.shift_2.pk) 

        # create a shift
        self.post_data_adm = {
            'start': '2012-07-10T10:00:00',
            'end': '2012-07-10T12:00:00',
            'title': 'testcl',
            'loc': 'Tech',
            'allDay': False,
            'color': 'Blue',
        }
        self.post_data_nml = {
            'start': '2012-07-10T12:00:00',
            'end': '2012-07-10T14:00:00',
            'title': 'testcon',
            'loc': 'Tech',
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
                        ['start', 'end', 'allDay', 'title', 'id', 'loc', 'color', 'resource_uri', 'for_trade', 'been_traded'])

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

    def setUp(self):
        super(PlannerBlockResourceTest, self).setUp()

        self.testcl = ConleaderFactory.create().user
        self.testcon = ConsultantFactory.create().user

        self.pb_1 = PlannerBlockFactory.create()
        self.pb_2 = PlannerBlockFactory.create()
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
