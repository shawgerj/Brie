from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile, PlannerBlock, TimeclockRecord, TimeclockAction
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
import pdb

def home(request):
    return render(request, 'ricotta/home.html',
                  {"worker": request.user.username,
                   "lab": request.user.profile.lab})

def clockin(request):
    ta = TimeclockAction.objects.filter(employee=request.user)

    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        real_ip = request.META['REMOTE_ADDR']

    if (ta):
        TimeclockRecord(start_time=ta[0].time,
                        end_time=timezone.now(),
                        employee=request.user,
                        inIP=ta[0].IP,
                        outIP=real_ip).save()
        ta.delete()
    else:
        TimeclockAction(time=timezone.now(),
                        employee=request.user,
                        IP=real_ip).save()
    return HttpResponseRedirect('/')

def whos_clockin(request):
    clocked_in = TimeclockAction.objects.all()

    return render(request, 'ricotta/whos_clockin.html',
                  {"clocked_in": clocked_in,
                   "title": "Who's Clocked In"})

def calendar_base(request):
    calendars = Location.objects.all()
    return render(request, 'ricotta/calendar_none.html',
                  {"calendars": calendars})

def calendar(request, location_name):
    get_object_or_404(Location, pk=location_name)

    return render(request, 'ricotta/calendar.html',
                  {"location_name": location_name,
                   "worker": request.user})

def trade_summary(request):
    return render(request, 'ricotta/trade_summary.html',
                  {"worker": request.user})

def planner(request, username):
    get_object_or_404(User, username=username)

    return render(request, 'ricotta/planner.html',
                  {"worker": request.user,
                   "preferences": PlannerBlock.PLANNER_CHOICES})

def planner_lab(request, location_name):
    get_object_or_404(Location, pk=location_name)
    workers = UserProfile.objects.filter(lab=location_name)

    return render(request, 'ricotta/planner_lab.html',
                  {"workers": workers,
                   "location_name": location_name})

def timeclock(request, username, pastperiod=0):
    pastperiod = int(pastperiod)
    # the 5 hours correction is for UTC time
    next_sat = timezone.now().replace(hour=0, minute=0, second=0, microsecond = 0) + timedelta(5 - timezone.now().weekday())
    start_bound = next_sat - timedelta(weeks=pastperiod * 2) - timedelta(weeks=2, days=1, hours=5)
    end_bound = next_sat - timedelta(weeks=pastperiod * 2)
    tr_data = TimeclockRecord.objects.filter(employee=request.user).filter(start_time__range=(start_bound, end_bound))
    sh_data = Shift.objects.filter(worker=request.user).filter(start_time__range=(start_bound, end_bound))

    # I bet there's a more clever way of doing this. One-liner perhaps?
    total_clocked = timedelta(0)
    for tr in tr_data:
        total_clocked += (tr.end_time - tr.start_time)

    # and here too
    total_scheduled = timedelta(0)
    for sh in sh_data:
        total_scheduled += (sh.end_time - sh.start_time)


    return render(request, 'ricotta/timeclock.html',
                  {"worker": request.user.username,
                   "tr_data": tr_data,
                   "total_scheduled": round(total_scheduled.total_seconds() / 3600, 2),
                   "total_clocked": round(total_clocked.total_seconds() / 3600, 2),
                   "title": "Timeclock for " + request.user.username,
                   "pastperiod": pastperiod})

def shifts(request, username):
    shift_data = Shift.objects.filter(worker=request.user).filter(start_time__range=(timezone.now(), timezone.now() + timedelta(weeks=1)))

    return render(request, 'ricotta/shift.html',
                  {"worker": request.user.username,
                   "shift_data": shift_data})

def employees(request):
    conleaders = User.objects.all().filter(is_staff=True)
    consultants = User.objects.all().exclude(is_staff=True)

    return render(request, 'ricotta/employees.html',
                  {"consultants": consultants,
                   "conleaders": conleaders,
                   "title": "All Employees"})

def employees_by_lab(request, location_name):
    conleaders = User.objects.filter(userprofile__lab=location_name).filter(is_staff=True)
    consultants = User.objects.filter(userprofile__lab=location_name).exclude(is_staff=True)

    return render(request, 'ricotta/employees.html',
                  {"consultants": consultants,
                   "conleaders": conleaders,
                   "title": "Employees in " + location_name})
