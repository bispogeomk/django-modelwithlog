# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-11 14:26
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import log_models.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GenericModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('number', models.PositiveSmallIntegerField()),
                ('file', models.FileField(blank=True, null=True, upload_to='temp/file')),
                ('json', jsonfield.fields.JSONField(default=dict)),
                ('text', models.TextField()),
                ('boolean', models.BooleanField(default=False)),
                ('real', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', log_models.models.ManagerWithLog()),
            ],
        ),
    ]
