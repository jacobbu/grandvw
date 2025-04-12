from django.contrib import admin
from .models import Video, YOLOModel

admin.site.register(YOLOModel)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'rtsp', 'created_at')