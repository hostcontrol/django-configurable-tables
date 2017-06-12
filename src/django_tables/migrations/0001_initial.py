# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TableConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('table_class', models.CharField(max_length=255)),
                ('columns', jsonfield.fields.JSONField(default='[]')),
                ('order_by', models.CharField(max_length=255, null=True)),
                ('limit', models.PositiveIntegerField(null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'table_configuration',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tableconfiguration',
            unique_together=set([('user', 'name')]),
        ),
    ]
