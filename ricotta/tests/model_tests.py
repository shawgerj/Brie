from django.test import TestCase, Client
import datetime
from django.utils.timezone import utc
from ricotta.models import Listserv, Location, DisciplineRecord, Shift, PlannerBlock, TimeclockRecord, TimeclockAction
from django.contrib.auth.models import User

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
