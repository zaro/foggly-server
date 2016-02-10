# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_dockercontainer_dockerimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='domainmodel',
            name='app_type',
            field=models.CharField(default='php7-mysql', max_length=20, choices=[('php7-mysql', 'PHP 7 / MySQL'), ('php7-postgre', 'PHP 7 / PostgreSQL'), ('flask-mongo', 'Flask / Mongo'), ('django-postgre', 'Django / PostgreSQL')]),
        ),
    ]
