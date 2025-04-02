from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path("data/", include('data.urls')),
    path("video/", include('video.urls', namespace='video')),
    path("admin/", admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout')
]
