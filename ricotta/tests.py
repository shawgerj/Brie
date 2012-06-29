from django.test import TestCase

class CalendarViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/calendar/tech/')
        self.assertEqual(resp.status_code, 200)
