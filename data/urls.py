from django.urls import path

from . import views


app_name = 'data'


urlpatterns = [
    path("add-figure", views.Add_Figure, name='add_figure')
]