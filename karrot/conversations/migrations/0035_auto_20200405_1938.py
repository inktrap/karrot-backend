# Generated by Django 3.0.2 on 2020-04-05 19:38

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('conversations', '0034_conversationmeta_threads'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='conversationparticipant',
            unique_together={('user', 'conversation')},
        ),
    ]
