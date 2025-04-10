from django import forms
from .models import Video
from .models import YOLOModel  # adjust if your model is elsewhere

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['name', 'rtsp', 'yolo_model']  # Add yolo_model

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(VideoForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['yolo_model'].queryset = YOLOModel.objects.filter(created_by=user)
