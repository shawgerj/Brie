from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from ricotta.models import Location, Shift, UserProfile, PlannerBlock
import urllib

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']
        allowed_methods = ['get']
        filtering = {
            'username': ALL,
        }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle = None):
        kwargs = {
            'resource_name': self._meta.resource_name, 
            'api_name': self._meta.api_name,
        } 
        if (bundle != None):
            kwargs['pk'] = bundle.obj.username
            return reverse('api_dispatch_detail', kwargs = kwargs)
        else:
            return reverse('api_dispatch_list', kwargs=kwargs)

class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        resource_name = 'location'
        fields = ['location_name', 'ip_address', 'enable_schedule']
        allowed_methods = ['get']
        include_resource_uri = False
        filtering = {
            'location_name': ALL,
        }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<location_name>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class ShiftResource(ModelResource):
    location_name = fields.ForeignKey(LocationResource, 'location_name')
    worker = fields.ForeignKey(UserResource, 'worker')
    class Meta:
        queryset = Shift.objects.all()
        resource_name = 'shift'
        authorization = Authorization()
        fields = ['start_time', 'end_time', 'location_name', 'worker', 
                  'resource_uri', 'for_trade', 'been_traded']
        allowed_methods = ['get', 'post', 'patch', 'delete', 'put']
        filtering = {
            'location_name': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        # see if there's a better way to rename fields than creating and 
        # deleting
        ### these four are required for fullCalendar.js
        bundle.data['start'] = bundle.data['start_time']
        bundle.data['end'] = bundle.data['end_time']
        bundle.data['allDay'] = False
        bundle.data['title'] = bundle.obj.worker
        ### and this next one is useful...
        bundle.data['id'] = bundle.data['resource_uri']
        bundle.data['location_name'] = bundle.obj.location_name
        bundle.data['color'] = 'blue' if bundle.data['for_trade'] == False else 'red'

        bundle.data.__delitem__('start_time')
        bundle.data.__delitem__('end_time')
        bundle.data.__delitem__('worker')
        return bundle

    def hydrate(self, bundle):
        bundle.data['start_time'] = bundle.data['start']
        bundle.data['end_time'] = bundle.data['end']
        bundle.data['location_name'] = "/api/v1/location/Tech/"
        bundle.data['worker'] = "/api/v1/user/" + bundle.data['title'] + "/"
        return bundle

class PlannerBlockResource(ModelResource):
    worker = fields.ForeignKey(UserResource, 'worker')
    class Meta:
        queryset = PlannerBlock.objects.all()
        resource_name = 'planner_block'
        authorization = Authorization()
        fields = ['start_time', 'end_time', 'block_type', 'worker', 
                  'resource_uri']
        allowed_methods = ['get', 'post', 'patch', 'delete', 'put']
        filtering = {
            'worker': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['start'] = bundle.data['start_time']
        bundle.data['end'] = bundle.data['end_time']
        bundle.data['allDay'] = False
        bundle.data['title'] = bundle.obj.get_block_type_display()
        bundle.data['id'] = bundle.data['resource_uri']

        bundle.data.__delitem__('start_time')
        bundle.data.__delitem__('end_time')
        return bundle

    def hydrate(self, bundle):
        bundle.data['start_time'] = bundle.data['start']
        bundle.data['end_time'] = bundle.data['end']
        return bundle

