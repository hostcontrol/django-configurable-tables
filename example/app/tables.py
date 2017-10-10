from __future__ import absolute_import

from django_tables import Table
from django_tables.column import TextColumn


class CustomerTable(Table):

    first_name = TextColumn()
    last_name = TextColumn()
    email_address = TextColumn()

    class Meta:
        default_columns = ['first_name', 'last_name']

