# Generated by Django 5.0.6 on 2024-07-17 02:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0009_alter_event_categories_alter_event_tags_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="groupmembers",
            name="is_moderator",
            field=models.BooleanField(default=False),
        ),
    ]