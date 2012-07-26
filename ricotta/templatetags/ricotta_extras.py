from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def datetime_diff(t1, t2):
    """Returns the result of the difference between two datetimes in hours"""
    return round((t2 - t1).total_seconds() / 3600, 2)
