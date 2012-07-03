from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile, PlannerBlock
from django.http import HttpResponse
from django.db.models import Count

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

def calendar(request, location_name):
    t = loader.get_template('ricotta/calendar.html')
    c = RequestContext(request, {
        'location_name': location_name,
    })
    return HttpResponse(t.render(c))

def planner(request, username):
    t = loader.get_template('ricotta/planner.html')
    c = RequestContext(request, {
            'user': username,
            'preferences': PlannerBlock.PLANNER_CHOICES,
    })
    return HttpResponse(t.render(c))
