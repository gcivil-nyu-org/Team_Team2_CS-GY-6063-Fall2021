# Generated by Django 3.2.8 on 2021-11-05 11:31

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Restroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yelp_id', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('accessible', models.BooleanField(default=False)),
                ('family_friendly', models.BooleanField(default=False)),
                ('transaction_not_required', models.BooleanField(default=False)),
                ('title', models.CharField(default='Restroom', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('headline', models.TextField(max_length=65)),
                ('comment', models.TextField(max_length=500)),
                ('restroom_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='naturescall.restroom')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
