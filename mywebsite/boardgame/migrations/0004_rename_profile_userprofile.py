# Generated by Django 5.0.6 on 2024-06-28 20:29

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0003_remove_event_slug"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Profile",
            new_name="UserProfile",
        ),
    ]
