from django.db import models

from accounts.models import User

class Video(models.Model):
    name = models.CharField(max_length=255)
    rtsp = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name='videos', on_delete=models.CASCADE)
    created_at = models.TimeField(auto_now_add=True)

class Detection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera = models.ForeignKey(Video, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)