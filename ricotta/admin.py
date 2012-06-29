from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from models import UserProfile

from ricotta.models import Listserv
from ricotta.models import Location
from ricotta.models import Shift
from ricotta.models import WorkedBy
from ricotta.models import DisciplineRecord

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
        self.inlines = [ProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)


    # inlines = [ProfileInline,]
    # def lab(self, obj):
    #     try:
    #         return obj.get_profile().get_lab_display()
    #     except UserProfile.DoesNotExist:
    #         return ''
    
    # list_display = UserAdmin.list_display + ('lab',)
    # search_fields = UserAdmin.search_fields + ('userprofile__lab',)

class WorkedByInline(admin.TabularInline):
    model = WorkedBy
    extra = 2

class ShiftAdmin(admin.ModelAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(ShiftAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [WorkedByInline]
        return super(ShiftAdmin, self).change_view(*args, **kwargs)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Listserv)
admin.site.register(Location)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(DisciplineRecord)
admin.site.register(WorkedBy)
