from django.conf.urls import patterns, include, url
from tastypie.api import Api
from ricotta.api import UserResource, LocationResource, ShiftResource, PlannerBlockResource

v1_api = Api(api_name = 'v1')
v1_api.register(UserResource())
v1_api.register(LocationResource())
v1_api.register(ShiftResource())
v1_api.register(PlannerBlockResource())


urlpatterns = patterns('',
    url(r'^$', 'ricotta.views.home'),
    url(r'^api/', include(v1_api.urls)),
    
    url(r'^locations/$', 'ricotta.views.locations'),
    url(r'^shifts/(?P<username>\w+)/$', 'ricotta.views.shifts_by_user'), 
                       
    url(r'^calendar/$', 'ricotta.views.calendar_base', name='calendar-home'),
    url(r'^calendar/(?P<location_name>.*)/$', 'ricotta.views.calendar'),
    url(r'^planner/(?P<username>\w+)/$', 'ricotta.views.planner'),
    url(r'^planner/lab/(?P<location_name>\w+)/$', 'ricotta.views.planner_lab'),
)
