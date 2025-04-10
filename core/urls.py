from django.urls import path
from django.contrib.auth.views import LogoutView
from custom_logic.views import user_dashboard

from . import views

app_name = 'core'


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('dashboard/', user_dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
   
]