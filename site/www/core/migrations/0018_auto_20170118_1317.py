# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-18 13:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_delete_dockerimage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DockerContainer',
            new_name='ContainerRuntime',
        ),
    ]