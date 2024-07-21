# Generated by Django 5.0.6 on 2024-07-18 02:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0016_auto_20240718_0219"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="nomination_status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Approved", "Approved"),
                    ("Rejected", "Rejected"),
                    ("Deleted", "Deleted"),
                ],
                default="Pending",
                max_length=10,
            ),
        ),
    ]