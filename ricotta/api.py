from django.conf.urls import url
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource
from ricotta.models import Location, Shift, UserProfile
import urllib

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']
        allowed_methods = ['get']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        resource_name = 'location'
        fields = ['location_name', 'ip_address', 'enable_schedule']
        allowed_methods = ['get']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<location_name>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class ShiftResource(ModelResource):
    location_name = fields.ForeignKey(LocationResource, 'location_name', 
                                      full=True)
    worker = fields.ForeignKey(UserResource, 'worker')
    class Meta:
        queryset = Shift.objects.all()
        resource_name = 'shift'
        authorization = Authorization()
        fields = ['start_time', 'end_time', 'location_name', 'num_owners', 
                  'worker']
        allowed_methods = ['get', 'post', 'patch', 'delete']

    def dehydrate(self, bundle):
        bundle.data['start'] = bundle.data['start_time']
        bundle.data['end'] = bundle.data['end_time']
        bundle.data['allDay'] = False
        bundle.data['title'] = bundle.obj.worker

        bundle.data.__delitem__('start_time')
        bundle.data.__delitem__('end_time')
        return bundle

    def hydrate(self, bundle):
        bundle.data['start_time'] = bundle.data['start']
        bundle.data['end_time'] = bundle.data['end']
        bundle.data['location_name'] = "/api/v1/location/" + bundle.data['location_name'] + "/"
        return bundle       
