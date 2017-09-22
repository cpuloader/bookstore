# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 08:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='picture',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='book',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='books', to=settings.AUTH_USER_MODEL),
        ),
    ]
