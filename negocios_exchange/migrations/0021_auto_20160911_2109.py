# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-12 01:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('negocios_exchange', '0020_transaction_confirm_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bank',
            name='balance',
            field=models.FloatField(default=0, null=True),
        ),
    ]
