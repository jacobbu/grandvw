from django.core.management.base import BaseCommand
from django.utils.timezone import timedelta
from django.utils import timezone
from datetime import timedelta
from video.models import Event
from custom_logic.models import UserEventAssignment, DailySummary, EventDefinition, CustomMetricCard, DailySummarySubscription
from django.contrib.auth import get_user_model
from openai import OpenAI
import os
from collections import defaultdict

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate a summary of the previous day\'s events for all users or a specific user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username of the user to generate a summary for'
        )

    def handle(self, *args, **options):
        now_mt = timezone.localtime()
        today = now_mt.date()
        summary_date = today - timedelta(days=1)
        username = options.get('user')

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if username:
            try:
                users = [sub.user for sub in DailySummarySubscription.objects.select_related("user")]
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"❌ No user found with username: {username}"))
                return
        else:
            users = User.objects.all()

        for user in users:
            if DailySummary.objects.filter(user=user, date=summary_date).exists():
                self.stdout.write(self.style.NOTICE(f"📄 Summary for {summary_date} already exists for {user.username}"))
                continue

            assigned_event_types = CustomMetricCard.objects.filter(
                user=user
            ).values_list('event_type', flat=True)

            events = Event.objects.filter(
                user=user,
                timestamp__date=summary_date,
                event_type__in=assigned_event_types
            )

            event_counts = defaultdict(int)
            event_details = defaultdict(list)

            for event in events:
                event_counts[event.event_type] += 1
                event_details[event.event_type].append({
                    "time": timezone.localtime(event.timestamp).strftime('%I:%M %p'),
                    "camera": event.camera.name,
                    "people": event.people,
                    "details": event.details,
                })

            summary_data = {
                "event_counts": dict(event_counts),
                "event_details": dict(event_details),
            }

            system_prompt = (
                "You are an employee summarizing the previous day's activity for your manager. "
                "Your goal is to give a clear, professional update on operational events, trends, and anything notable. "
                "Use a confident, concise tone and avoid restating raw data."
            )

            # Get the user's business knowledge
            knowledge = getattr(user.knowledge_base, "content", "")

            user_prompt = f"""User: {user.username}
            Date: {summary_date}

            User's Business Knowledge:
            {knowledge}

            Yesterday's Event Data:
            - Event Counts: {dict(event_counts)}
            - Event Details: {dict(event_details)}

            Write a short paragraph summarizing yesterday's activity for a manager. Highlight any patterns, errors, or observations from the event data. The tone should reflect the user’s business priorities and goals where relevant."""

            
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                )

                summary_text = response.choices[0].message.content

                DailySummary.objects.create(
                    user=user,
                    date=summary_date,
                    summary_text=summary_text,
                    raw_data=summary_data,
                    generated_by="daily_script"
                )

                self.stdout.write(self.style.SUCCESS(f"✅ Summary saved for {user.username} ({summary_date})"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error generating summary for {user.username}: {e}"))
