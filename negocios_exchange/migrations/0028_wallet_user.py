# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-24 03:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('negocios_exchange', '0027_auto_20161020_0309'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userw', to=settings.AUTH_USER_MODEL),
        ),
    ]
