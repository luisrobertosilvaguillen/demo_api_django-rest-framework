# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-08 01:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('negocios_exchange', '0033_bank_account_dni'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_Type',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='bank',
            name='account_email',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='bank',
            name='account_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='negocios_exchange.Account_Type'),
        ),
    ]
