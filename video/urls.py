from django.urls import path

from . import views


app_name = 'video'


urlpatterns = [
    path('', views.videos, name='videos'),
    path('add-video/', views.Add_Video, name='add_video'),
    path('edit-video/<int:video_id>/', views.edit_video, name='edit_video'),
    path('delete-video/<int:video_id>/', views.delete_video, name='delete_video'),
    path('stream/<int:video_id>/', views.stream_video, name='stream_video'),
]