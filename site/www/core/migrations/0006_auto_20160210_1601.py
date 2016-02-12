# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_domainmodel_app_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontainer',
            name='container_id',
            field=models.CharField(default='zaro/php7', max_length=100),
        ),
        migrations.AddField(
            model_name='dockercontainer',
            name='description',
            field=models.CharField(default='Apache 2.4 / PHP 7.0', max_length=200),
        ),
        migrations.AlterField(
            model_name='domainmodel',
            name='app_type',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, to='core.DockerContainer'),
        ),
    ]
