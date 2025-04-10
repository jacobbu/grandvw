from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class EventDefinition(models.Model):
    name = models.CharField(max_length=255)
    import_path = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class GraphDefinition(models.Model):
    name = models.CharField(max_length=255)
    import_path = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserEventAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_def = models.ForeignKey(EventDefinition, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} → {self.event_def}"

class UserGraphAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    graph_def = models.ForeignKey(GraphDefinition, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} → {self.graph_def}"
    
PAGE_CHOICES = [
    ('charts', 'Charts Page'),
    ('dashboard', 'Dashboard'),
    ('profile', 'User Profile'),
]

CARD_SIZE_CHOICES = [
    ('sm', 'Small'),
    ('md', 'Medium'),
    ('lg', 'Large'),
    ('xl', 'Extra Large'),
    ('full', 'Full Width'),
]

class CustomChart(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="charts")
    chart_type = models.CharField(max_length=50, default="bar")
    config_code = models.TextField(help_text="Python code that sets `chart_config` as a Chart.js config dict.")
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    pages = models.JSONField(default=list)  # e.g., ["dashboard", "charts"]
    card_size = models.CharField(max_length=10, choices=CARD_SIZE_CHOICES, default='md')

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class CustomMetricCard(models.Model):
    CARD_PERIOD_CHOICES = [
        ("today", "Today"),
        ("month", "Last 30 Days"),
        ("year", "Last 365 Days"),
    ]

    EVENT_CHOICES = [
        ("KIT_SUCCESS", "KIT_SUCCESS"),
        ("KIT_ERROR", "KIT_ERROR"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255, choices=EVENT_CHOICES)
    period = models.CharField(max_length=10, choices=CARD_PERIOD_CHOICES)
    emoji = models.CharField(max_length=5, blank=True, help_text="Optional emoji or icon")
    color_class = models.CharField(max_length=50, default="bg-gray-50")

    def __str__(self):
        return f"{self.user.username}: {self.title} ({self.event_type} - {self.period})"