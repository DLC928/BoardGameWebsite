# Generated by Django 5.0.6 on 2024-07-20 17:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0021_vote"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="vote",
            unique_together=set(),
        ),
    ]
