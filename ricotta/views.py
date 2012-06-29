from django.template import RequestContext, Context, loader
from ricotta.models import Shift, Location, UserProfile
from django.http import HttpResponse
from django.db.models import Count

def shifts(request):
    shift_list = Shift.objects.all()
    t = loader.get_template('ricotta/shifts.html')
    c = Context({
        'shift_list': shift_list,
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
