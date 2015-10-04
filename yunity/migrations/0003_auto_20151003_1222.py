# -*- coding: utf-8 -*-
# Generated by Django 1.9a1 on 2015-10-03 12:22
from __future__ import unicode_literals

from django.db import migrations
from yunity.models import Category

initial_categories = ("user.default","valuable.default","opportunity.default")

def create_initial_categories(apps, schema_editor):
    for name in initial_categories:
        Category.objects.create(name=name)

def remove_initial_categories(apps, schema_editor):
    Category.objects.filter(name__in=initial_categories).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('yunity', '0002_auto_20151003_1204'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, reverse_code=remove_initial_categories)
    ]