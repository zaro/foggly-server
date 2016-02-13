# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20160213_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontainer',
            name='proxy_type',
            field=models.CharField(choices=[('http', 'HTTP'), ('uWSGI', 'uWSGI'), ('FastCGI', 'FastCGI')], max_length=50, default='http'),
        ),
    ]
