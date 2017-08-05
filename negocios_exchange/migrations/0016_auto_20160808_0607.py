# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-08 10:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('negocios_exchange', '0015_auto_20160808_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction_log',
            name='cashier',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]