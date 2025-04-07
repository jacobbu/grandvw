from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from custom_logic.views import user_dashboard
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path("data/", include('data.urls')),
    path("video/", include('video.urls', namespace='video')),
    path("admin/", admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include('custom_logic.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)