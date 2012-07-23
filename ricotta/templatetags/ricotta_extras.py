from django import template

register = template.Library()

@register.filter
def datetime_diff(t1, t2):
    """Returns the result of the difference between two datetimes"""
    return str(t2 - t1)
