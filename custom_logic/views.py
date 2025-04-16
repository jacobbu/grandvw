from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from video.models import Event, Detection
from django.utils.timezone import now, localtime, timedelta
from .models import CustomChart,CustomMetricCard
from custom_logic.utils import execute_chartjs_config, get_rendered_charts, send_sms
from custom_logic.models import EventDefinition, DetectionLabel, ModelPerformanceImage, SMSRecipient
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import get_object_or_404


@login_required
def user_dashboard(request):
    current_time = localtime()
    today = current_time.date()
    last_30_days = today - timedelta(days=30)
    last_year = today - timedelta(days=365)

    events_today = Event.objects.filter(user=request.user, timestamp__date=today)
    recent_events = Event.objects.filter(user=request.user).order_by('-timestamp')[:20]

    # Generate cards
    cards = []
    metric_cards = CustomMetricCard.objects.filter(user=request.user)
    for card in metric_cards:
        if card.period == "today":
            count = Event.objects.filter(user=request.user, timestamp__date=today, event_type=card.event_type).count()
        elif card.period == "Last 30 Days":
            count = Event.objects.filter(user=request.user, timestamp__date__gte=last_30_days, event_type=card.event_type).count()
        elif card.period == "Last 365 Days":
            count = Event.objects.filter(user=request.user, timestamp__date__gte=last_year, event_type=card.event_type).count()
        else:
            count = 0

        cards.append({
            "title": card.title,
            "count": count,
            "emoji": card.emoji or "",
            "color_class": card.color_class,
            "period": card.get_period_display(),
        })

    return render(request, 'core/dashboard.html', {
        'success_count': events_today.filter(event_type='KIT_SUCCESS').count(),
        'failure_count': events_today.filter(event_type='KIT_ERROR').count(),
        'events': recent_events,
        'cards': cards,  # ✅ Add this line
    })


@login_required
def user_charts_view(request):
    current_time = localtime()
    today = current_time.date()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    last_30_days = today - timedelta(days=30)
    last_year = today - timedelta(days=365)

    # Events for counts
    events_today = Event.objects.filter(user=request.user, timestamp__date=today)
    events_30 = Event.objects.filter(user=request.user, timestamp__date__gte=last_30_days)
    events_365 = Event.objects.filter(user=request.user, timestamp__date__gte=last_year)

    counts = {
        "today_success": events_today.filter(event_type='KIT_SUCCESS').count(),
        "today_error": events_today.filter(event_type='KIT_ERROR').count(),
        "month_success": events_30.filter(event_type='KIT_SUCCESS').count(),
        "month_error": events_30.filter(event_type='KIT_ERROR').count(),
        "year_success": events_365.filter(event_type='KIT_SUCCESS').count(),
        "year_error": events_365.filter(event_type='KIT_ERROR').count(),
    }

    # Dynamic event cards
    cards = []
    metric_cards = CustomMetricCard.objects.filter(user=request.user)
    for card in metric_cards:
        if card.period == "today":
            count = Event.objects.filter(user=request.user, timestamp__date=today, event_type=card.event_type).count()
        elif card.period == "month":
            count = Event.objects.filter(user=request.user, timestamp__date__gte=last_30_days, event_type=card.event_type).count()
        elif card.period == "year":
            count = Event.objects.filter(user=request.user, timestamp__date__gte=last_year, event_type=card.event_type).count()
        else:
            count = 0

        cards.append({
            "title": card.title,
            "count": count,
            "emoji": card.emoji or "",
            "color_class": card.color_class,
            "period": card.get_period_display()
        })

    # Charts
    context_data = {
        "user": request.user,
        "events": Event.objects.filter(user=request.user),
        "detections": Detection.objects.filter(user=request.user),
    }

    charts = []
    user_charts = CustomChart.objects.filter(user=request.user).filter(pages__contains=["charts"])

    for chart in user_charts:
        try:
            chart_config = execute_chartjs_config(chart.config_code, context_data)
            config_json = json.dumps(chart_config, cls=DjangoJSONEncoder) if isinstance(chart_config, dict) else "{}"
            charts.append({
                "name": chart.name,
                "config": config_json,
                "card_size": chart.card_size,
                "error": None,
            })
        except Exception as e:
            charts.append({
                "name": chart.name,
                "config": "{}",
                "card_size": chart.card_size,
                "error": str(e),
            })

    return render(request, "charts/user_charts.html", {
        "charts": charts,
        "cards": cards,
        **counts,
    })

@login_required
def technical_overview(request):
    user = request.user

    assigned_event_defs = EventDefinition.objects.filter(usereventassignment__user=user).distinct()

    detections = DetectionLabel.objects.filter(user=user)
    graphs = CustomChart.objects.filter(user=user)

    sms_alerts = SMSRecipient.objects.filter(user=user)

    model_performance_images = ModelPerformanceImage.objects.filter(user=user)

    context = {
        "events": assigned_event_defs,
        "detections": detections,
        "graphs": graphs,
        "sms_alerts": sms_alerts,
        "model_performance_images": model_performance_images,
    }
    return render(request, "charts/technical_overview.html", context)

@login_required
def event_detail(request, slug):
    event = get_object_or_404(EventDefinition, slug=slug)
    return render(request, "charts/event_detail.html", {"event": event})

@login_required
def label_detail(request, label_id):
    label = get_object_or_404(DetectionLabel, id=label_id, user=request.user)
    return render(request, "charts/label_detail.html", {"label": label})

@login_required
def model_performance_detail(request, image_id):
    image = get_object_or_404(ModelPerformanceImage, id=image_id, user=request.user)
    return render(request, "charts/model_performance_detail.html", {"image_obj": image})

from .models import SMSRecipient
from django.shortcuts import get_object_or_404

@login_required
def sms_recipient_detail(request, recipient_id):
    recipient = get_object_or_404(SMSRecipient, id=recipient_id, user=request.user)
    example_event_type = recipient.event_types[0] if recipient.event_types else "EVENT_TYPE"
    example_message = f"Event Alert: {example_event_type} at 2025-04-15 12:34:56"

    return render(request, "charts/sms_recipient_detail.html", {
        "recipient": recipient,
        "example_message": example_message
    })

@login_required
def chart_detail(request, slug):
    chart = get_object_or_404(CustomChart, slug=slug, user=request.user)

    context_data = {
        "user": request.user,
        "events": Event.objects.filter(user=request.user),
        "detections": Detection.objects.filter(user=request.user),
    }

    try:
        raw_config = execute_chartjs_config(chart.config_code, context_data)
        chart_config = json.dumps(raw_config, cls=DjangoJSONEncoder) if isinstance(raw_config, dict) else "{}"
    except Exception as e:
        print("❌ Error executing chart config:", e)
        chart_config = "{}"

    return render(request, "charts/chart_detail.html", {
        "chart": chart,
        "chart_config": chart_config,
    })


