from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

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

class Shift(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location_name = models.ForeignKey(Location)
    worker = models.ForeignKey(User, null=True)
    for_trade = models.BooleanField()
    been_traded = models.BooleanField()

    def __unicode__(self):
        return self.location_name.location_name + ' ' + self.start_time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + self.worker.username

class TimeclockRecord(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    inIP = models.IPAddressField()
    outIP = models.IPAddressField()
    employee = models.ForeignKey(User)

# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# post_save.connect(create_user_profile, sender=User)
