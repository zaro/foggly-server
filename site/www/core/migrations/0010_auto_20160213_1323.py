# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20160212_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareddatabase',
            name='db_type',
            field=models.CharField(max_length=50, choices=[('mysql', 'MySQL'), ('postgre', 'PostgreSQL'), ('mongo', 'Mongo'), ('couchdb', 'CouchDB')]),
        ),
    ]
