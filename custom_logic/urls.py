from django.urls import path
from .views import user_dashboard
from .views import user_charts_view

urlpatterns = [
    path('user-dashboard/', user_dashboard, name='user_dashboard'),
    path("charts/", user_charts_view, name="user_charts"),
]