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
        return self.location_name.location_name + ' ' + self.start_time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + self.worker.username

    class Meta:
        permissions = (
            ("trade_shift", "Put own shift up for trade"),
            ("take_shift", "Take a shift that is up for trade"),
        )
            

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
        return self.worker.username + ' ' + self.start_time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + self.get_block_type_display()

    class Meta:
        permissions = (
            ("change_pb", "Change own planner block"),
            ("delete_pb", "Delete own planner block"),
            ("view_pb", "View own planner block"),
            ("view_pb_gl", "View any planner block"),
        )

class TimeclockRecord(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    inIP = models.IPAddressField()
    outIP = models.IPAddressField()
    employee = models.ForeignKey(User)

    class Meta:
        permissions = (
            ("view_tr", "View own timeclock record"),
            ("view_tr_gl", "View any timeblock record"),
        )
