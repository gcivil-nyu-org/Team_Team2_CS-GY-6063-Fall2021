# Generated by Django 3.2.9 on 2021-11-13 14:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("naturescall", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClaimedRestroom",
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
                ("verified", models.BooleanField(default=False)),
                (
                    "restroom_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="naturescall.restroom",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
