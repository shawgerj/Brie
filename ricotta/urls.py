from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'ricotta.views.home'),
    url(r'^clockin/$', 'ricotta.views.clockin', name='clock-in'),

    url(r'^calendar/$', 'ricotta.views.calendar_base', name='calendar-home'),
    url(r'^calendar/(?P<location_name>.*)/$', 'ricotta.views.calendar'),
    url(r'^shifts/(?P<username>\w+)/$', 'ricotta.views.shifts', name='my-shifts'),
    url(r'^planner/(?P<username>\w+)/$', 'ricotta.views.planner', name='edit-own-planner'),
    url(r'^planner/lab/(?P<location_name>\w+)/$', 'ricotta.views.planner_lab'),

    url(r'^timeclock/(?P<username>\w+)/$', 'ricotta.views.timeclock', name='view-timeclock'),
    url(r'^timeclock/(?P<username>\w+)/(?P<pastperiod>\d+)/$', 'ricotta.views.timeclock', name='view-timeclock'),
    url(r'^whos_clockin/$', 'ricotta.views.whos_clockin', name='whos-clockin'),

    url(r'^employees/$', 'ricotta.views.employees', name='employees'),
    url(r'^employees/(?P<location_name>.*)/$', 'ricotta.views.employees_by_lab', name='employees-by-lab')
)
