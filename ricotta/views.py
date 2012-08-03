from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile, PlannerBlock, TimeclockRecord, TimeclockAction
from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
import pdb
import array

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

def calc_timeperiod(pastperiod):
    # the 5 hours correction is for UTC time
    next_sat = timezone.now().replace(hour=0, minute=0, second=0, microsecond = 0) + timedelta(5 - timezone.now().weekday())
    return {"start": next_sat - timedelta(weeks=pastperiod * 2) - timedelta(weeks=2, days=1, hours=5),
            "end": next_sat - timedelta(weeks=pastperiod * 2)}

def sum_timeclocks(data):
    return reduce(lambda h, e: h + (e.end_time - e.start_time),
                  data, timedelta(0))

def kronos_round(t):
    return round(t.total_seconds() / 3600, 2)

def timeclock(request, username, pastperiod=0):
    user = User.objects.get(username=username)
    period = calc_timeperiod(int(pastperiod))
    tr_data = user.timeclockrecord_set.filter(start_time__range=(period['start'], period['end']))
    sh_data = user.shift_set.filter(start_time__range=(period['start'], period['end']))

    total_clocked = sum_timeclocks(tr_data)
    total_scheduled = sum_timeclocks(sh_data)

    return render(request, 'ricotta/timeclock.html',
                  {"worker": user.username,
                   "tr_data": tr_data,
                   "total_scheduled": kronos_round(total_scheduled),
                   "total_clocked": kronos_round(total_clocked),
                   "title": "Timeclock for " + user.username,
                   "pastperiod": pastperiod})

def timeclocks_all(request, pastperiod=0):
    period = calc_timeperiod(int(pastperiod))

    users = User.objects.all()
    clockin_data = []
    for u in users:
        total_clocked = sum_timeclocks(u.timeclockrecord_set.filter(start_time__range=(period['start'], period['end'])))
        total_scheduled = sum_timeclocks(u.shift_set.filter(start_time__range=(period['start'], period['end'])))

        clockin_data.append({"user": u,
                             "total_clocked": kronos_round(total_clocked),
                             "total_scheduled": kronos_round(total_scheduled)})

    return render(request, 'ricotta/timeclocks_all.html',
                  {"timeclock_data": clockin_data})


def shifts(request, username):
    shift_data = Shift.objects.filter(worker=request.user).filter(start_time__range=(timezone.now(), timezone.now() + timedelta(weeks=1)))

    return render(request, 'ricotta/shift.html',
                  {"worker": request.user.username,
                   "shift_data": shift_data})

class EmployeesView(ListView):
    template_name = 'ricotta/employees.html'
    context_object_name='user_queryset'

    def separate_groups(self, q):
        return {"conleaders": q.filter(is_staff=True),
                "consultants": q.exclude(is_staff=True)}
    
    def get_queryset(self):
        try:
            self.kwargs['location_name']
        except:
            return self.separate_groups(User.objects.all())
        else:
            return self.separate_groups(User.objects.filter(userprofile__lab=self.kwargs['location_name']))

    def get_context_data(self, **kwargs):
        context = super(EmployeesView, self).get_context_data(**kwargs)
        try:
            self.kwargs['location_name']
        except:
            context['title'] = "All Employees"
        else:
            context['title'] = "Employees in " + self.kwargs['location_name']
        return context
