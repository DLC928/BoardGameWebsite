# Generated by Django 5.0.6 on 2024-07-22 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "boardgame",
            "0023_userprofile_categories_userprofile_favorite_games_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="UserLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("city", models.CharField(max_length=100)),
                ("sublocality", models.CharField(blank=True, max_length=100)),
                ("state", models.CharField(blank=True, max_length=100)),
                ("postcode", models.CharField(blank=True, max_length=20)),
                ("country", models.CharField(max_length=100)),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                (
                    "user_profile",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="boardgame.userprofile",
                    ),
                ),
            ],
        ),
    ]
