# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_delete_servertask'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('domain_name', models.CharField(max_length=200)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='domain',
            name='user',
        ),
        migrations.DeleteModel(
            name='Domain',
        ),
    ]
