from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.db import models
from jsonfield import JSONField


class TableConfiguration(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=255)
    table_class = models.CharField(max_length=255)
    columns = JSONField(default='[]')
    order_by = models.CharField(max_length=255, null=True)
    limit = models.PositiveIntegerField(null=True)

    class Meta(object):
        db_table = 'table_configuration'
        unique_together = ('user', 'name')
        app_label = 'django_tables'

    def __unicode__(self):
        return 'Configuration for {} table'.format(self.name)
