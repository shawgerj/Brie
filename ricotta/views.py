from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile, PlannerBlock
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.db.models import Count

def home(request):
    t = loader.get_template('ricotta/home.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c))
            
def shifts_by_user(request, username):
    shift_list = Shift.objects.filter(worker__username__exact=username).order_by('start_time')
    t = loader.get_template('ricotta/shifts.html')
    c = Context({
        'shift_list': shift_list,
        'user': username,
    })
    return HttpResponse(t.render(c))

def locations(request):
    user_lab_count = UserProfile.objects.values('lab').annotate(Count('lab'))
    
    t = loader.get_template('ricotta/locations.html')
    c = Context({
            'user_lab_count': user_lab_count,
    })
    return HttpResponse(t.render(c))

def calendar_base(request):
    calendars = Location.objects.all()
    t = loader.get_template('ricotta/calendar_none.html')
    c = RequestContext(request, {
            'calendars': calendars,
            })
    return HttpResponse(t.render(c))

def calendar(request, location_name):
    try:
        l = Location.objects.get(pk=location_name)
    except:
        raise Http404
    else:
        t = loader.get_template('ricotta/calendar.html')
        c = RequestContext(request, {
                'location_name': location_name,
            })
        return HttpResponse(t.render(c))

def planner(request, username):
    try:
        User.objects.get(username=username)
    except:
        raise Http404
    else:
        t = loader.get_template('ricotta/planner.html')
        c = RequestContext(request, {
                'worker': username,
                'preferences': PlannerBlock.PLANNER_CHOICES,
            })
        return HttpResponse(t.render(c))

def planner_lab(request, location_name):
    try:
        Location.objects.get(pk=location_name)
    except:
        raise Http404
    else:
        workers = UserProfile.objects.filter(lab=location_name)
        
        t = loader.get_template('ricotta/planner_lab.html')
        c = RequestContext(request, {
                'workers': workers,
                'location_name': location_name
            })
        return HttpResponse(t.render(c))
