import factory
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from ricotta.models import UserProfile, Location, Shift, DisciplineRecord, Listserv, PlannerBlock, TimeclockRecord, TimeclockAction
import datetime
from django.utils import timezone

# build instead of create by default
factory.Factory.default_strategy = factory.BUILD_STRATEGY

################
# Group and Users
###########################

class GroupFactory(factory.Factory):
    FACTORY_FOR = Group

class ConleaderGroupFactory(GroupFactory):
    name = 'Conleader'

class ConsultantGroupFactory(GroupFactory):
    name = 'Consultant'

class TestGroupFactory(GroupFactory):
    name = 'Test'

class UserFactory(factory.Factory):
    FACTORY_FOR = User

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
#        group = GroupFactory.create(name='Con')
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        user.set_password(password)
#        user.groups.add(group)
        if create:
            user.save()
        return user

# post create the group upon save. I'm getting lunch....
    
class ProfileFactory(factory.Factory):
    FACTORY_FOR = UserProfile

    user = factory.SubFactory(UserFactory)

    # @classmethod
    # def _prepare(cls, create, **kwargs):
    #     lab = kwargs.pop('lab', None)
    #     profile = super(ProfileFactory, cls)._prepare(create, **kwargs)
    #     profile.lab = Location.objects.get(location_name=lab)
    #     if create:
    #         profile.save()
    #     return profile
    

class ConleaderFactory(ProfileFactory):
    user__username = 'testcl'
    user__password = 'testcl'
    user__is_staff = True
    user__is_active = True
    lab = Location.objects.get(location_name="Tech")
    
#    user__groups = factory.SubFactory(ConleaderGroupFactory)


class ConsultantFactory(ProfileFactory):
    user__username = 'testcon'
    user__password = 'testcon'
    user__is_staff = False
    user__is_active = True
    lab = Location.objects.get(location_name="Tech")


################
# Shift
###########################

class ShiftFactory(factory.Factory):
    FACTORY_FOR = Shift
    
    for_trade = False
    been_traded = False
    start_time = timezone.now()
    end_time = timezone.now() + datetime.timedelta(hours=1)


################
# PlannerBlock
###########################

class PlannerBlockFactory(factory.Factory):
    FACTORY_FOR = PlannerBlock

    start_time = timezone.now()
    end_time = timezone.now() + datetime.timedelta(hours=1)


################
# TimeclockRecord
###########################

class TimeclockRecordFactory(factory.Factory):
    FACTORY_FOR = TimeclockRecord
    
    inIP = '127.0.0.1'
    outIP = '127.0.0.1'
    start_time = timezone.now()
    end_time = timezone.now() + datetime.timedelta(hours=1)

################
# TimeclockAction
###########################

class TimeclockActionFactory(factory.Factory):
    FACTORY_FOR = TimeclockAction
    
    IP = '127.0.0.1'

################
# DisciplineRecord
###########################

class DisciplineRecordFactory(factory.Factory):
    FACTORY_FOR = DisciplineRecord

################
# Listserv
###########################

class ListservFactory(factory.Factory):
    FACTORY_FOR = Listserv

