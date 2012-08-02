from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.models import User

urlpatterns = patterns('',
    url(r'^$', 'ricotta.views.home'),
    url(r'^clockin/$', 'ricotta.views.clockin', name='clock-in'),

    url(r'^calendar/$', 'ricotta.views.calendar_base', name='calendar-home'),
    url(r'^calendar/trade_summary/$', 'ricotta.views.trade_summary', name='trade-summary'),
    url(r'^calendar/(?P<location_name>.*)/$', 'ricotta.views.calendar'),
    url(r'^shifts/(?P<username>\w+)/$', 'ricotta.views.shifts', name='my-shifts'),
    url(r'^planner/(?P<username>\w+)/$', 'ricotta.views.planner', name='edit-own-planner'),
    url(r'^planner/lab/(?P<location_name>\w+)/$', 'ricotta.views.planner_lab'),

    url(r'^timeclock/(?P<username>\w+)/$', 'ricotta.views.timeclock', name='view-timeclock'),
    url(r'^timeclock/(?P<username>\w+)/(?P<pastperiod>\d+)/$', 'ricotta.views.timeclock', name='view-timeclock'),
    url(r'^timeclocks_all/$', 'ricotta.views.timeclocks_all', name='timeclocks-all'),
    url(r'^whos_clockin/$', 'ricotta.views.whos_clockin', name='whos-clockin'),

    url(r'^employees/$', 'ricotta.views.employees', name='employees'),
    url(r'^employees/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=User,
            template_name='ricotta/employee.html',
            context_object_name = 'user_object'),
        name='employee-detail'),
    url(r'^employees/(?P<location_name>.*)/$', 'ricotta.views.employees_by_lab', name='employees-by-lab'),
)
