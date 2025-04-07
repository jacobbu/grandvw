from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from video.models import Event

def index(request):
    return render(request, 'core/index.html')


def about(request):
    return render(request, 'core/about.html')


@login_required
def dashboard(request):
    recent_events = Event.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'core/dashboard.html', {'events': recent_events})