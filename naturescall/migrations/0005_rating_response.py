# Generated by Django 3.2.9 on 2021-11-28 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("naturescall", "0004_coupon_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="rating",
            name="response",
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
