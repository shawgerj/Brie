from django.conf.urls import patterns, include, url
from tastypie.api import Api
from ricotta.api import UserResource, LocationResource, ShiftResource, WorkedByResource

from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name = 'v1')
v1_api.register(UserResource())
v1_api.register(LocationResource())
v1_api.register(ShiftResource())
v1_api.register(WorkedByResource())

#workedby_resource = WorkedByResource()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    
#    url(r'^api/(?P<username>\w+)/', include(workedby_resource.urls)),
    url(r'^locations/$', 'ricotta.views.locations'),
    url(r'^shifts/$', 'ricotta.views.shifts'), 
    url(r'^calendar/(?P<location_name>.*)/$', 'ricotta.views.calendar'),
#    url(r'^discipline/$', ...)
)
