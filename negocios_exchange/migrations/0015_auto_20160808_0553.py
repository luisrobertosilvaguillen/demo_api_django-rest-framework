# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-08 09:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('negocios_exchange', '0014_auto_20160808_0537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='cashier',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cashier', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='negocios_exchange.Wallet'),
        ),
    ]