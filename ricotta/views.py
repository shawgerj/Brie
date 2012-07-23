from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile, PlannerBlock, TimeclockRecord
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

def home(request):
    return render(request, 'ricotta/home.html', 
                  {"worker": request.user.username,
                   "lab": request.user.profile.lab})
            
def shifts_by_user(request, username):
    shift_list = Shift.objects.filter(worker__username__exact=username).order_by('start_time')

    return render(request, 'ricotta/shifts.html', 
                  {"shift_list": shift_list,
                   "user": username})

def locations(request):
    user_lab_count = UserProfile.objects.values('lab').annotate(Count('lab'))

    return render(request, 'ricotta/locations.html',
                  {"user_lab_count": user_lab_count})

def calendar_base(request):
    calendars = Location.objects.all()
    return render(request, 'ricotta/calendar_none.html', 
                  {"calendars": calendars})

def calendar(request, location_name):
    get_object_or_404(Location, pk=location_name)

    return render(request, 'ricotta/calendar.html', 
                  {"location_name": location_name})

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
    tr_data = TimeclockRecord.objects.filter(employee=request.user)

    return render(request, 'ricotta/timeclock.html',
                  {"worker": request.user.username,
                   "tr_data": tr_data})

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
