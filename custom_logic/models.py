from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

class EventDefinition(models.Model):
    name = models.CharField(max_length=255)
    import_path = models.CharField(max_length=255)
    event_definition_code = models.TextField(blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    

class SMSRecipient(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sms_recipients')
    phone_number = models.CharField(max_length=15)
    event_types = models.JSONField(default=list)
    message_template = models.TextField(
        blank=True,
        help_text=(
            "Custom message format. You can use these placeholders: "
            "{event_type}, {timestamp}, {camera}, {user}, {gif_url}"
        )
    )

    def __str__(self):
        return f"{self.phone_number} for {self.user.username}"

    def render_message(self, event):
        context = {
            "event_type": event.event_type,
            "timestamp": event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "camera": event.camera.name if event.camera else "Unknown Camera",
            "user": event.user.username,
            "gif_url": event.gif.url if event.gif else None,
        }

        if self.message_template:
            return self.message_template.format(**context)

        message = f"[grandvw.io] {context['event_type']} at {context['timestamp']} on {context['camera']}."
        if context["gif_url"]:
            message += f" View: {context['gif_url']}"
        return message
    
class DetectionLabel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    description = models.TextField()
    image_with_box = models.ImageField(upload_to="label_examples/", blank=True, null=True)
    
class ModelPerformanceImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to="model_performance/")

class DailySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField(default=timezone.now)
    
    # Natural language summary for display
    summary_text = models.TextField()

    # Optional: structured data used to generate the summary
    raw_data = models.JSONField(blank=True, null=True)

    # Optional: system notes or generation metadata
    generated_by = models.CharField(max_length=255, default='auto', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Summary for {self.user.username} on {self.date}"
    
class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[("user", "User"), ("assistant", "Assistant")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class UserKnowledgeBase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="knowledge_base")
    content = models.TextField(help_text="Static business knowledge (goals, org chart, SOPs, etc.)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Knowledge for {self.user.username}"
    
class DailySummarySubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s daily summary subscription"