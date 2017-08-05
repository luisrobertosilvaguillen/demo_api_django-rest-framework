# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-11 07:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('negocios_exchange', '0018_auto_20160911_0022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction_Confirm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('quantity', models.FloatField(default=0)),
                ('code_confirmation', models.CharField(default='', max_length=50)),
                ('financial_entity', models.CharField(default='', max_length=80)),
            ],
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='code_confirmation_cashier',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='code_confirmation_user',
        ),
        migrations.AddField(
            model_name='transaction_confirm',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='negocios_exchange.Transaction'),
        ),
        migrations.AddField(
            model_name='transaction_confirm',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_confirm', to=settings.AUTH_USER_MODEL),
        ),
    ]