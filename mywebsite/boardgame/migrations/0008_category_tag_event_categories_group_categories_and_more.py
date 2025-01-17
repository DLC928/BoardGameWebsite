# Generated by Django 5.0.6 on 2024-07-15 19:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0007_alter_game_thumbnail_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="event",
            name="categories",
            field=models.ManyToManyField(
                related_name="events", to="boardgame.category"
            ),
        ),
        migrations.AddField(
            model_name="group",
            name="categories",
            field=models.ManyToManyField(
                related_name="groups", to="boardgame.category"
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="tags",
            field=models.ManyToManyField(related_name="events", to="boardgame.tag"),
        ),
        migrations.AddField(
            model_name="group",
            name="tags",
            field=models.ManyToManyField(related_name="groups", to="boardgame.tag"),
        ),
    ]
