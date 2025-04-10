from django.contrib import admin
from .models import Video, YOLOModel  # Assuming YOLOModel is in video.models

admin.site.register(Video)
admin.site.register(YOLOModel)