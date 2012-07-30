from django.test import TestCase, Client
import datetime
from django.utils.timezone import utc
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord, TimeclockAction
from django.contrib.auth.models import User

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
