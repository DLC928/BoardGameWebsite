# Generated by Django 5.0.6 on 2024-07-16 02:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0008_category_tag_event_categories_group_categories_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="categories",
            field=models.ManyToManyField(
                blank=True, related_name="events", to="boardgame.category"
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="events", to="boardgame.tag"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="categories",
            field=models.ManyToManyField(
                blank=True, related_name="groups", to="boardgame.category"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="groups", to="boardgame.tag"
            ),
        ),
    ]
