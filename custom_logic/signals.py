from django.db.models.signals import post_save
from django.dispatch import receiver
from video.models import Event
from .models import SMSRecipient
from custom_logic.utils import send_sms

@receiver(post_save, sender=Event)
def notify_sms_recipients(sender, instance, created, **kwargs):
    if not created:
        return

    recipients = SMSRecipient.objects.filter(user=instance.user)
    for recipient in recipients:
        if instance.event_type in recipient.event_types:
            message = f"Event Alert: {instance.event_type} at {instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            send_sms(recipient.phone_number, message)
