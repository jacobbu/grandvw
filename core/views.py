from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from video.models import Event
from django.db.models.functions import TruncDate
from django.utils.timezone import now

def index(request):
    return render(request, 'core/index.html')


def about(request):
    return render(request, 'core/about.html')


@login_required
def dashboard(request):
    today = now().date()

    recent_events = Event.objects.filter(user=request.user).order_by('-timestamp')[:20]

    # Today's events for success/failure count
    events_today = Event.objects.annotate(date=TruncDate('timestamp')).filter(date=today, user=request.user)
    success_count = events_today.filter(event_type='KIT_SUCCESS').count()
    failure_count = events_today.filter(event_type='KIT_ERROR').count()

    context = {
        'events': recent_events,
        'success_count': success_count,
        'failure_count': failure_count,
    }

    return render(request, 'core/dashboard.html', context)