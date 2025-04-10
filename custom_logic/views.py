from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from video.models import Event, Detection
from django.utils.timezone import now, localtime, timedelta
from .models import CustomChart,CustomMetricCard
from custom_logic.utils import execute_chartjs_config, get_rendered_charts
from django.core.serializers.json import DjangoJSONEncoder
import json


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