# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-11 04:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('negocios_exchange', '0017_auto_20160910_1704'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='wallet_1',
            new_name='wallet',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='wallet_2',
        ),
    ]
