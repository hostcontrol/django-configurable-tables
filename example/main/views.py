from __future__ import absolute_import

import django_tables

from main.models import Customer
from main.tables import CustomerTable


class Main(django_tables.ConfigurableTableView):

    model = Customer
    table_class = CustomerTable
