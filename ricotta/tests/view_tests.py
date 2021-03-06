from django.test import TestCase, Client
import datetime
from django.utils import timezone
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord, TimeclockAction
from ricotta.tests.factories import *
from django.contrib.auth.models import User
import pdb

class HomeViewTestCase(TestCase):

    def setUp(self):
        self.con = ConsultantFactory.create().user
        self.client.login(username=self.con.username, password='testcon')

    def test_homepage(self):
        resp = self.client.get('/ricotta/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)
        self.assertTrue('lab' in resp.context)

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

    def test_calendar_none_view(self):
        resp = self.client.get('/ricotta/calendar/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('calendars' in resp.context)
        self.assertEqual(resp.context[-1]['calendars'].count(), 6)

class PlannerViewsTestCase(TestCase):
    def test_planner_detail(self):
        consultant = ConsultantFactory.create().user
        conleader = ConleaderFactory.create().user
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

class TimeclockViewsTestCase(TestCase):
    # a little explanation here. I'm going to test for the following... URLs
    # should be modified later to match
    # when a user views /ricotta/timeclock/<user>, they should see their own
    # timeclock. They should not be able to see any other users
    # a conleader or admin should have access to /ricotta/timeclock/<user>/edit
    # to view/modify anybody's timeclock. These URLs should not be accessible
    # for ordinary users

    def setUp(self):
        self.con = ConsultantFactory.create().user
        TimeclockRecordFactory.create(employee=self.con)
        self.client.login(username=self.con.username, password='testcon')

    def test_timeclock_view(self):
        resp = self.client.get('/ricotta/timeclock/testcon/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('tr_data' in resp.context)
        self.assertEqual(resp.context[-1]['tr_data'].count(), 1)

class EmployeeViewsTestCase(TestCase):

    def setUp(self):
        self.con = ConsultantFactory.create().user
        self.cl = ConleaderFactory.create().user
        self.client.login(username=self.con.username, password='testcon')

    def test_employees_all_view(self):
        resp = self.client.get('/ricotta/employees/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('user_queryset' in resp.context)
        self.assertEqual(resp.context[-1]['user_queryset']['conleaders'].count(), 1)
        self.assertEqual(resp.context[-1]['user_queryset']['consultants'].count(), 1)
        self.assertEqual(resp.context[-1]['title'], "All Employees")

    def test_employees_lab(self):
        resp = self.client.get('/ricotta/employees/Tech/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('user_queryset' in resp.context)
        self.assertEqual(resp.context[-1]['user_queryset']['conleaders'].count(), 1)
        self.assertEqual(resp.context[-1]['user_queryset']['consultants'].count(), 1)
        self.assertEqual(resp.context[-1]['title'], "Employees in Tech")

        resp = self.client.get('/ricotta/employees/IC-Main/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('user_queryset' in resp.context)
        self.assertEqual(resp.context[-1]['user_queryset']['conleaders'].count(), 0)
        self.assertEqual(resp.context[-1]['user_queryset']['consultants'].count(), 0)
        self.assertEqual(resp.context[-1]['title'], "Employees in IC-Main")

class ClockInTestCase(TestCase):

    def setUp(self):
        self.con = ConsultantFactory.create().user
        self.cl = ConleaderFactory.create().user
        self.client = Client(HTTP_X_FORWARDED_FOR = '127.0.0.1')
        self.client.login(username=self.con.username, password='testcon')

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
        t = timezone.now()
        # create a clock-in record so we can clock out two hours later
        ta_in = TimeclockActionFactory.create(
            employee=self.con, time=(t - datetime.timedelta(hours=2)))

        resp = self.client.get('/ricotta/clockin/')
        self.assertEqual(resp.status_code, 302)
        ta = TimeclockAction.objects.all()

        # the one we created above should have been removed.
        self.assertEqual(ta.count(), 0)

        tr = TimeclockRecord.objects.all()
        # and we should have one timeclock records
        self.assertEqual(tr.count(), 1)
        tr_1 = tr[0]
        self.assertEqual(tr_1.employee.username, 'testcon')
        # just test for 7200 seconds (2 hours). There are some microseconds
        # we don't need to worry about
        self.assertEqual((tr_1.end_time - tr_1.start_time).seconds, 7200)

    def test_whos_clockin(self):
        # clock in two users
        t = timezone.now()
        
        ta_in = TimeclockActionFactory.create(
            employee=self.con, time=(t - datetime.timedelta(hours=2)))
        ta_in = TimeclockActionFactory.create(
            employee=self.cl, time=(t - datetime.timedelta(hours=2)))

        # now test the page
        resp = self.client.get('/ricotta/whos_clockin/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('clocked_in' in resp.context)
        self.assertEqual(resp.context[-1]['clocked_in'].count(), 2)
