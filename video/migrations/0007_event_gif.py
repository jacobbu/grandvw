# Generated by Django 5.2 on 2025-04-07 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("video", "0006_event_thumbnail"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="gif",
            field=models.FileField(blank=True, null=True, upload_to="event_gifs/"),
        ),
    ]
