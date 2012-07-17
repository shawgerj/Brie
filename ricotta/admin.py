from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from models import UserProfile

from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey

from ricotta.models import Listserv, Location, Shift, DisciplineRecord, PlannerBlock

class ProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    max_num = 1              

class CustomUserAdmin(UserAdmin):
    def lab(self, obj):
        return obj.get_profile().lab
    
    list_display = ('username', 'first_name', 'last_name', 'email', 'lab', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__lab__location_name')

    def add_view(self, *args, **kwargs): 
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [ProfileInline, ApiKeyInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Listserv)
admin.site.register(Location)
admin.site.register(DisciplineRecord)
admin.site.register(Shift)
admin.site.register(PlannerBlock)
#admin.site.register(ApiKey)
admin.site.register(ApiAccess)
