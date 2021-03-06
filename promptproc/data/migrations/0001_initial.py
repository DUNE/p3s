# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-03 11:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(default='', max_length=36)),
                ('name', models.CharField(default='', max_length=64)),
                ('dirpath', models.CharField(default='', max_length=256)),
                ('state', models.CharField(default='', max_length=64)),
                ('comment', models.CharField(default='', max_length=256)),
                ('datatype', models.CharField(default='', max_length=64)),
                ('datatag', models.CharField(default='', max_length=64)),
                ('wf', models.CharField(default='', max_length=64)),
                ('wfuuid', models.CharField(default='', max_length=36)),
                ('source', models.CharField(default='', max_length=36)),
                ('target', models.CharField(default='', max_length=36)),
                ('sourceuuid', models.CharField(default='', max_length=36)),
                ('targetuuid', models.CharField(default='', max_length=36)),
                ('ts_reg', models.DateTimeField(blank=True, null=True, verbose_name='ts_reg')),
                ('ts_upd', models.DateTimeField(blank=True, null=True, verbose_name='ts_upd')),
            ],
        ),
        migrations.CreateModel(
            name='datatype',
            fields=[
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('ext', models.CharField(default='', max_length=8)),
                ('comment', models.CharField(default='', max_length=256)),
            ],
        ),
    ]
