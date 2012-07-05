import datetime
from django.test import TestCase
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord
from django.contrib.auth.models import User

class ListservModelTestCase(TestCase):
    def test_listserv(self):
        self.l1 = Listserv.objects.create(email='tech@listserv.it.northwestern.edu')
        
        self.assertEquals(self.l1.email, 'tech@listserv.it.northwestern.edu')

class DisciplineRecordTestCase(TestCase):
    fixtures = ['ricotta_testusers.yaml']
    def test_disciplinerecord(self):
        self.d1 = DisciplineRecord.objects.create(date_of_record=datetime.datetime.now(), employee = User.objects.get(pk=2), changed_by = User.objects.get(pk=1), status_name = 'nd', comment = 'this is a comment')
        
        self.assertEquals(self.d1.employee.username, 'nmlusr')
        self.assertEquals(self.d1.changed_by.username, 'admusr')

class ShiftTestCase(TestCase):
    fixtures = ['ricotta_testusers.yaml']
    def test_shift(self):
        time = datetime.datetime.now()
        self.s1 = Shift.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), location_name = Location.objects.get(pk='Tech'), worker = User.objects.get(pk=1), for_trade = False, been_traded = False)
        self.s2 = Shift.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), location_name = Location.objects.get(pk='Tech'), worker = User.objects.get(pk=2), for_trade = True, been_traded = True)

        self.assertEquals(self.s1.for_trade, False)
        self.assertEquals(self.s2.for_trade, True)
        self.assertEquals(self.s1.worker.username, 'admusr')
        self.assertEquals(self.s2.worker.username, 'nmlusr')

class PlannerBlockTestCase(TestCase):
    fixtures = ['ricotta_testusers.yaml']
    def test_plannerblock(self):
        time = datetime.datetime.now()
        self.pb1 = PlannerBlock.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), worker = User.objects.get(pk=1), block_type = 'pf')
        
        self.assertEquals(self.pb1.worker.username, 'admusr')
        self.assertEquals(self.pb1.end_time - self.pb1.start_time, datetime.timedelta(hours=1))
        self.assertEquals(self.pb1.get_block_type_display(), "Preferred")

class TimeclockRecordTestCase(TestCase):
    fixtures = ['ricotta_testusers.yaml']
    def test_timeclockrecord(self):
        time = datetime.datetime.now()
        loc = Location.objects.get(pk='Tech')
        self.tr1 = TimeclockRecord.objects.create(start_time=time, end_time=time + datetime.timedelta(hours=1), inIP = loc.ip_address, outIP = loc.ip_address, employee = User.objects.get(pk=1))

        self.assertEquals(self.tr1.employee.username, 'admusr')
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
    fixtures = ['ricotta_testusers', 'ricotta_planners_testdata.yaml']

    def test_planner_detail(self):
        # check to make sure both of these planners exist
        resp = self.client.get('/planner/admusr/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)
        resp = self.client.get('/planner/nmlusr/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('worker' in resp.context)

        # and if we try a user that doesn't exist, return 404
        resp = self.client.get('/planner/notusr/')
        self.assertEqual(resp.status_code, 404)
        
        
