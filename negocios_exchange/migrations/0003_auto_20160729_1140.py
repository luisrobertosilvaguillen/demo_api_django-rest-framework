# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-29 15:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('negocios_exchange', '0002_token_verification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_profile',
            name='group',
        ),
        migrations.AlterField(
            model_name='user_profile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]