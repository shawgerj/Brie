import factory
from django.contrib.auth.models import User
from ricotta.models import UserProfile, Location, Shift, DisciplineRecord, Listserv, PlannerBlock, TimeclockRecord, TimeclockAction
import datetime
from django.utils import timezone

# build instead of create by default
factory.Factory.default_strategy = factory.BUILD_STRATEGY

################
# Users
###########################
class UserFactory(factory.Factory):
    FACTORY_FOR = User

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user
    
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

    # @classmethod
    # def _prepare(cls, create, **kwargs):
    #     lab = kwargs.pop('lab', None)
    #     profile = super(ConleaderFactory, cls)._prepare(create, **kwargs)
    #     profile.lab = Location.objects.get(location_name=lab)
    #     if create:
    #         profile.save()
    #     return profile


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

