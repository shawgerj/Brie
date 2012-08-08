from django.test import TestCase, Client
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from ricotta.models import Location
from ricotta.tests.factories import * 


class ListservModelTestCase(TestCase):
    def test_listserv(self):
        l1 = ListservFactory(email='tech@listserv.it.northwestern.edu')
        
        self.assertEquals(l1.email, 'tech@listserv.it.northwestern.edu')

class DisciplineRecordTestCase(TestCase):
    def test_disciplinerecord(self):
        consultant = ConsultantFactory()
        conleader = ConleaderFactory()
        d1 = DisciplineRecordFactory(
            employee = consultant.user, changed_by = conleader.user)
        
        self.assertEquals(d1.employee.username, 'testcon')
        self.assertEquals(d1.changed_by.username, 'testcl')

class ShiftTestCase(TestCase):
    def test_shift(self):
        time = timezone.now()
        
        consultant = ConsultantFactory()
        conleader = ConleaderFactory()
        s1 = ShiftFactory(start_time=time, end_time= time + datetime.timedelta(hours=1), worker = conleader.user)
        s2 = ShiftFactory(start_time=time, end_time= time + datetime.timedelta(hours=1), worker = consultant.user, for_trade = True, been_traded = True)

        self.assertEquals(s1.for_trade, False)
        self.assertEquals(s2.for_trade, True)
        self.assertEquals(s1.worker.username, 'testcl')
        self.assertEquals(s2.worker.username, 'testcon')

class PlannerBlockTestCase(TestCase):
    def test_plannerblock(self):
        time = timezone.now()
        
        conleader = ConleaderFactory()
        pb1 = PlannerBlockFactory(worker = conleader.user, block_type = 'pf')
        
        self.assertEquals(pb1.worker.username, 'testcl')
        self.assertEquals(pb1.end_time - pb1.start_time, datetime.timedelta(hours=1))
        self.assertEquals(pb1.get_block_type_display(), "Preferred")

class TimeclockRecordTestCase(TestCase):
    def test_timeclockrecord(self):
        time = timezone.now()
        loc = Location.objects.get(pk='Tech')
        conleader = ConleaderFactory()

        tr1 = TimeclockRecordFactory(start_time=time, end_time=time + datetime.timedelta(hours=1), employee = conleader.user)

        self.assertEquals(tr1.employee.username, 'testcl')
        self.assertEquals(tr1.end_time - tr1.start_time, datetime.timedelta(hours=1))
        self.assertEquals(tr1.inIP, tr1.outIP)

class TimeclockActionTestCase(TestCase):
    def test_timeclockaction(self):
        t = timezone.now()
        conleader = ConleaderFactory()
        ta1 = TimeclockActionFactory(time=t, employee = conleader.user)

        self.assertEquals(ta1.employee.username, 'testcl')
        self.assertEquals(ta1.time, t)
        self.assertEquals(ta1.IP, '127.0.0.1')


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
