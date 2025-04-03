from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import VideoForm
from .models import Video

@login_required

def videos(request):
    videos = Video.objects.filter(created_by=request.user)

    return render(request, 'video/videos.html', {
        'videos': videos,
    })

def Add_Video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)

        if form.is_valid():
            video = form.save(commit=False)
            video.created_by = request.user
            video.save()

            return redirect('video:videos')
    else:
        form = VideoForm()

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
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            return redirect('video:videos')
    else:
        form = VideoForm(instance=video)
    return render(request, 'video/edit_video.html', {'form': form, 'video': video})

def stream_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, created_by=request.user)
    return render(request, 'video/stream_video.html', {'video': video})
