# Generated by Django 5.0.6 on 2024-07-11 19:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0004_grouplocation_postcode"),
    ]

    operations = [
        migrations.AddField(
            model_name="grouplocation",
            name="sublocality",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="grouplocation",
            name="postcode",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
