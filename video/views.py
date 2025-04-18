from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import os

from .forms import VideoForm
from .models import Video, Event

@login_required

@login_required
def videos(request):
    videos = Video.objects.filter(created_by=request.user).select_related('yolo_model')

    for video in videos:
        latest_event = Event.objects.filter(camera=video, user=request.user).order_by('-timestamp').first()

        if latest_event and latest_event.gif:
            video.latest_gif_url = latest_event.gif.url
        else:
            video.latest_gif_url = None

    return render(request, 'video/videos.html', {
        'videos': videos,
    })

def Add_Video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, user=request.user)

        if form.is_valid():
            video = form.save(commit=False)
            video.created_by = request.user
            video.save()

            return redirect('video:videos')
    else:
        form = VideoForm(user=request.user)

    return render(request, 'video/add_video.html', {
        'form': form,
    })

def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, created_by=request.user)
    if request.method == 'POST':
        video.delete()
        return redirect('video:videos')
    return render(request, 'video/confirm_delete.html', {'video': video})

def edit_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, created_by=request.user)
    if request.method == "POST":
        form = VideoForm(request.POST, instance=video, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('video:videos')
    else:
        form = VideoForm(instance=video, user=request.user)
    return render(request, 'video/edit_video.html', {'form': form, 'video': video})

@login_required
def stream_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, created_by=request.user)

    ws_base_url = os.environ.get('WS_BASE_URL')

    return render(request, "video/stream_video.html", {
        "video": video,
        "ws_base_url": ws_base_url,
    })

@login_required
def dashboard(request):
    recent_events = Event.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'dashboard.html', {'events': recent_events})