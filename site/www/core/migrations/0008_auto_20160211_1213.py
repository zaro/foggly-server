# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0007_databaseuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedDatabase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
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
        migrations.RemoveField(
            model_name='databaseuser',
            name='user',
        ),
        migrations.DeleteModel(
            name='DatabaseUser',
        ),
    ]
