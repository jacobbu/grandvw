from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from video.models import Event

@login_required
def user_dashboard(request):
    recent_events = Event.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'dashboard.html', {'events': recent_events})
