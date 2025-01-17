# Generated by Django 5.0.6 on 2024-07-20 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0017_game_nomination_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="admin_only_nominations",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="nominations_open",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="event",
            name="signups_open",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="skip_nominations",
            field=models.BooleanField(default=False),
        ),
    ]
