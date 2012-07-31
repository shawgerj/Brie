from django import template
from datetime import datetime, timedelta
from ricotta.models import Shift, Location
from django.utils import timezone

register = template.Library()

@register.filter
def datetime_diff(t1, t2):
    """Returns the result of the difference between two datetimes in hours"""
    return round((t2 - t1).total_seconds() / 3600, 2)

@register.filter
def ip_to_lab(ip):
    """Returns the name of a lab based on the given IP address"""
    if ip == "127.0.0.1":
        return "Localhost"
    else:
        return Location.objects.all().filter(ip_address=ip)[0].location_name

@register.filter
def next_shift(tr):
    """Accepts a timeclock record and gets the next shift"""
    if tr.IP == "127.0.0.1":
        return "None"
    else:
        l = Location.objects.all().get(ip_address=tr.IP).location_name
        s = Shift.objects.all().filter(location_name=l).filter(start_time__gt=timezone.now())[0]
        return ' '.join((s.worker.first_name,
                         s.worker.last_name,
                         'at',
                         s.start_time.astimezone(timezone.get_default_timezone()).strftime("%m-%d %H:%M:%S %p")))
