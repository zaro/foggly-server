# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160211_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domainmodel',
            name='app_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DockerContainer'),
        ),
    ]
