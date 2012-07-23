from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from tastypie.models import create_api_key

class Listserv(models.Model):
    email = models.CharField(max_length=50, primary_key=True)
    
    def __unicode__(self):
        return self.email

class Location(models.Model):
    location_name = models.CharField(max_length=20, primary_key=True)
    address = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    ip_address = models.IPAddressField()
    enable_schedule = models.BooleanField()
    
    def __unicode__(self):
        return self.location_name

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phone_number = models.CharField(max_length=12)
    lab = models.ForeignKey(Location, blank=True)
    listservs = models.ManyToManyField(Listserv, blank=True)
    
    def __unicode__(self):
        return self.user.username

User.profile = property(lambda u: UserProfile.objects.get(user=u))

class DisciplineRecord(models.Model):
    STATUS_CHOICES = (
        ('nd', 'No Discipline'),
        ('vw', 'Verbal Warning'),
        ('wu', 'Write-Up'),
        ('pr', 'Probation'),
    )
    date_of_record = models.DateTimeField()
    employee = models.ForeignKey(User, related_name='disciplined_employee')
    changed_by = models.ForeignKey(User)
    status_name = models.CharField(max_length=3, choices = STATUS_CHOICES)
    comment = models.TextField()

    def __unicode__(self):
        return self.employee.username + ' ' + self.date_of_record.strftime("%y-%m-%d")

    class Meta:
        permissions = (
            ("view_dr", "View discipline record"),
        )

class Shift(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location_name = models.ForeignKey(Location)
    worker = models.ForeignKey(User, null=True)
    for_trade = models.BooleanField()
    been_traded = models.BooleanField()

    def __unicode__(self):
        return self.location_name.location_name + ' ' + self.start_time.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M:%S") + ' ' + self.worker.username
            
class PlannerBlock(models.Model):
    PLANNER_CHOICES = (
        ('pf', 'Preferred'),
        ('ic', 'In Class'),
        ('un', 'Unavailable'),
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    worker = models.ForeignKey(User, null=True)
    block_type = models.CharField(max_length=2, choices = PLANNER_CHOICES)

    def __unicode__(self):
        return self.worker.username + ' ' + self.start_time.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M:%S") + ' ' + self.get_block_type_display()


class TimeclockRecord(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    inIP = models.IPAddressField()
    outIP = models.IPAddressField()
    employee = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.employee.username + ' ' + self.start_time.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M:%S") + ' ' + self.inIP

# this is to generate the tastypie API keys for each user
models.signals.post_save.connect(create_api_key, sender=User)
