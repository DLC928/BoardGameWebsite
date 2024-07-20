# Generated by Django 5.0.6 on 2024-07-20 16:04

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0019_rename_nomination_gamesignup_game_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="gamesignup",
            old_name="game",
            new_name="nomination",
        ),
        migrations.AlterUniqueTogether(
            name="gamesignup",
            unique_together={("nomination", "user")},
        ),
    ]
