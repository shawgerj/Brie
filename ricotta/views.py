from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile, PlannerBlock, TimeclockRecord
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from datetime import datetime, timedelta

def home(request):
    return render(request, 'ricotta/home.html', 
                  {"worker": request.user.username,
                   "lab": request.user.profile.lab})
            
def calendar_base(request):
    calendars = Location.objects.all()
    return render(request, 'ricotta/calendar_none.html', 
                  {"calendars": calendars})

def calendar(request, location_name):
    get_object_or_404(Location, pk=location_name)

    return render(request, 'ricotta/calendar.html', 
                  {"location_name": location_name,
                   "worker": request.user})

def planner(request, username):
    get_object_or_404(User, username=username)

    return render(request, 'ricotta/planner.html',
                  {"worker": username, 
                   "preferences": PlannerBlock.PLANNER_CHOICES})

def planner_lab(request, location_name):
    get_object_or_404(Location, pk=location_name)
    workers = UserProfile.objects.filter(lab=location_name)
    
    return render(request, 'ricotta/planner_lab.html', 
                  {"workers": workers,
                   "location_name": location_name})

def timeclock(request, username):
    # this all needs to be queried on 2 week intervals eventually rather
    # than pulling the entire result set
    tr_data = TimeclockRecord.objects.filter(employee=request.user)
    sh_data = Shift.objects.filter(worker=request.user)

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
                   "total_clocked": round(total_clocked.total_seconds() / 3600, 2)})

def employees(request):
    employees = User.objects.all()

    return render(request, 'ricotta/employees.html', 
                  {"employees": employees, 
                   "title": "All Employees"})

def employees_by_lab(request, location_name):
    employees = User.objects.filter(userprofile__lab=location_name)
    
    return render(request, 'ricotta/employees.html', 
                  {"employees": employees,
                   "title": "Employees in " + location_name})
