# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-29 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='host',
            field=models.CharField(default='', max_length=32),
        ),
        migrations.AddField(
            model_name='job',
            name='site',
            field=models.CharField(default='', max_length=32),
        ),
    ]
