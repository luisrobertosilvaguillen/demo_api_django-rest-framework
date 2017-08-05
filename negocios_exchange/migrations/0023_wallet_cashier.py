# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-15 23:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('negocios_exchange', '0022_auto_20160913_2352'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet_Cashier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cashier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='negocios_exchange.Wallet')),
            ],
        ),
    ]