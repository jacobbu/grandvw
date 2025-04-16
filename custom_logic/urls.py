from django.urls import path
from .views import user_dashboard
from .views import user_charts_view
from .views import technical_overview
from .views import event_detail
from .views import label_detail
from .views import model_performance_detail
from .views import sms_recipient_detail
from .views import chart_detail

urlpatterns = [
    path('user-dashboard/', user_dashboard, name='user_dashboard'),
    path('technical-overview/', technical_overview, name='technical_overview'),
    path("charts/", user_charts_view, name="user_charts"),
    path("charts/<slug:slug>/", chart_detail, name="chart_detail"),
    path('events/<slug:slug>/', event_detail, name='event_detail'),
    path("labels/<int:label_id>/", label_detail, name="label_detail"),
    path("model-performance/<int:image_id>/", model_performance_detail, name="model_performance_detail"),
    path("sms-recipients/<int:recipient_id>/", sms_recipient_detail, name="sms_recipient_detail"),

]