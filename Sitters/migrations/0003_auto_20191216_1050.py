# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-16 10:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Sitters', '0002_auto_20191216_1036'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='Prices',
            new_name='Price',
        ),
    ]
