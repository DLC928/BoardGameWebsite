# Generated by Django 5.0.6 on 2024-07-15 04:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0005_rename_thumbnail_game_thumbnail_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="thumbnail_file",
            field=models.ImageField(
                default="boardgame/images/default_thumbnail.jpg",
                upload_to="game_thumbnails/",
            ),
        ),
    ]
