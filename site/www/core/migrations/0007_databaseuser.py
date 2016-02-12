# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_auto_20160210_1601'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('db_user', models.CharField(max_length=50)),
                ('db_pass', models.CharField(max_length=50)),
                ('db_name', models.CharField(max_length=50)),
                ('db_type', models.CharField(max_length=50)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
