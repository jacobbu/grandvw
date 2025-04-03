from django.db import models

from accounts.models import User

class Data(models.Model):
    name = models.CharField(max_length=255)
    fig = models.CharField(max_length=255)    # plotly figure
    created_by = models.ForeignKey(User, related_name='datas', on_delete=models.CASCADE),
    created_at = models.TimeField(auto_now_add=True)
