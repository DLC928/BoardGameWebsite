# Generated by Django 5.0.6 on 2024-07-15 04:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0004_game_thumbnail_url_alter_game_thumbnail"),
    ]

    operations = [
        migrations.RenameField(
            model_name="game",
            old_name="thumbnail",
            new_name="thumbnail_file",
        ),
    ]
