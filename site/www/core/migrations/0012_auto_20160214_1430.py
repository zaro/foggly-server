# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_dockercontainer_proxy_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontainer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 2, 14, 14, 30, 42, 288527, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dockercontainer',
            name='modified_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 14, 14, 30, 51, 616280, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dockercontainer',
            name='proxy_type',
            field=models.CharField(max_length=50, default='http', choices=[('http', 'HTTP'), ('uwsgi', 'uWSGI'), ('fastcgi', 'FastCGI')]),
        ),
    ]
