# Generated by Django 5.0.6 on 2024-07-11 19:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0005_grouplocation_sublocality_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventlocation",
            name="sublocality",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
