# Generated by Django 5.0.6 on 2024-06-30 18:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boardgame", "0004_alter_game_age_alter_game_weight"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="weight",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=4, null=True
            ),
        ),
    ]
