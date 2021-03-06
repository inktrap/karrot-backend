# Generated by Django 2.1.2 on 2018-12-07 22:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pickups', '0004_pickupdatecollector_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupdate',
            name='feedback_given_by',
            field=models.ManyToManyField(related_name='feedback_about_pickups', through='pickups.Feedback', to=settings.AUTH_USER_MODEL),
        ),
    ]
