from django.db import models
from django.core.files.storage import FileSystemStorage
from accounts.models import User

event_fs = FileSystemStorage(location='media/event_thumbnails')


class YOLOModel(models.Model):
    title = models.CharField(max_length=100)
    model_file = models.FileField(upload_to="yolo_models/")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

class Video(models.Model):
    name = models.CharField(max_length=255)
    rtsp = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name='videos', on_delete=models.CASCADE)
    created_at = models.TimeField(auto_now_add=True)
    yolo_model = models.ForeignKey(YOLOModel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title 


class Detection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera = models.ForeignKey(Video, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    EVENT_TYPES = [
        ("KIT_SUCCESS", "Avy Kit Packed Successfully"),
        ("KIT_ERROR", "Kit Packing Error"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera = models.ForeignKey("Video", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    people = models.CharField(max_length=255, blank=True, default="")
    details = models.TextField(blank=True, null=True)
    gif_thumb = models.ImageField(upload_to='event_gifs/thumbs/', storage=event_fs, null=True, blank=True)
    gif = models.FileField(upload_to='event_gifs/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_event_type_display()} @ {self.timestamp}"


