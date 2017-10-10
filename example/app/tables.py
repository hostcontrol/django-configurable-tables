from __future__ import absolute_import

from django_tables import Table
from django_tables.column import TextColumn, BooleanColumn, DateColumn


class CustomerTable(Table):

    first_name = TextColumn(sortable=True)
    last_name = TextColumn()
    email_address = TextColumn()
    has_paid = BooleanColumn()
    registered_at = DateColumn()

    class Meta:
        default_columns = ['first_name', 'last_name']
        default_order_by = 'first_name'
