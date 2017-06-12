from __future__ import unicode_literals, absolute_import

import copy
import re

from django.views.generic.edit import FormMixin
from django.utils.functional import cached_property

from django_tables.forms import TableConfigurationForm
from django_tables.models import TableConfiguration
from django_tables.paginator import DiggPaginator


class TableMixin(object):

    table_name = None
    table_class = None
    table_default_columns = None
    table_configuration_form_class = TableConfigurationForm

    def get_table_class(self):
        return self.table_class

    def get_table(self, table_class, columns, queryset, **kwargs):
        return table_class(visible_columns=columns or [], rows=queryset, **kwargs)

    def get_table_name_for_table_class(self, table_class):
        """
        Returns table name. This should be a unique name per table.
        """

        if self.table_name is not None:
            return self.table_name

        table_name = table_class.__name__
        table_name = re.sub('([A-Z])', r'-\1', table_name)

        # Strip leading dashes
        table_name = table_name.lstrip('-')

        # Convert to lowercase
        table_name = table_name.lower()

        # Strip the -table part (which inherits from the class name)
        if table_name.endswith('-table'):
            table_name = table_name[:-6]

        return table_name

    def get_table_configuration_form_initial(self, table_configuration):
        """
        Allows to set some initial values for the table configuration.
        """

        return {
            'name': table_configuration.name,
            'columns': table_configuration.columns,
            'order_by': table_configuration.order_by,
            'limit': table_configuration.limit
        }

    def get_table_configuration_form_kwargs(self, table_class, initial):
        """
        Allows customizable form kwargs.
        """
        return {
            'table_class': table_class,
            'initial': initial,
            'data': self.request.POST or None
        }

    def get_table_configuration_form_class(self):
        """
        Returns the form class to use to configure the table.
        """
        return self.table_configuration_form_class

    def get_table_configuration_form(self, form_class, form_kwargs):
        """
        Returns the initialized form.
        """
        return form_class(**form_kwargs)

    def get_table_configuration(self, table_class):
        """
        Returns the initialized table configuration model for this table.
        """

        if self.request.user.is_authenticated():
            table_configuration, created = TableConfiguration.objects.get_or_create(
                user=self.request.user,
                name=self.get_table_name_for_table_class(table_class=table_class),
                table_class=table_class.__name__,
                defaults={
                    'columns': self.get_default_columns(table_class=table_class)
                }
            )
        else:
            created = False
            table_configuration = TableConfiguration(
                name=self.get_table_name_for_table_class(table_class=table_class),
                table_class=table_class.__name__,
                columns=self.get_default_columns(table_class=table_class),
                limit=self.paginate_by if hasattr(self, 'paginate_by') else 20
            )

        return table_configuration, created

    def get_default_columns(self, table_class):

        default_columns = table_class._meta.default_columns

        if self.table_default_columns:
            default_columns = self.table_default_columns

        default_columns = copy.deepcopy(default_columns)
        default_columns.extend([name for name, column in table_class._meta.columns if column.is_always_visible])

        return default_columns

    def get_order_by(self):

        order_by = super(TableMixin, self).get_order_by()

        if order_by:
            return order_by

        table_class = self.get_table_class()
        table_configuration = self.get_table_configuration(table_class=table_class)

        return table_configuration.order_by

    def get_default_order_by(self):

        table_class = self.get_table_class()

        order_by = self.get_table_configuration(table_class=table_class).order_by

        if not order_by:
            return

        # Keep track of ascending or descending order
        desc = order_by.startswith('-')

        if desc:
            order_by = order_by[1:]

        order_by = table_class[order_by].order_by_column

        if desc:
            order_by = '-{}'.format(order_by)

        return order_by


class FilterMixin(FormMixin):

    """
    Allows filtering on POST requests. Classes should use the `get_filters`
    method to access the filters when validated properly by the form.
    """

    filter_form_class = None

    def get_form_kwargs(self):

        form_kwargs = super(FilterMixin, self).get_form_kwargs()

        form_kwargs['data'] = self.request.GET or None

        return form_kwargs

    def get_context_data(self, **kwargs):
        """
        Make the form available in the template context.
        """

        context_data = super(FilterMixin, self).get_context_data(**kwargs)

        if self.filter_form_class:
            context_data['form'] = self.form

        return context_data

    def get_filters(self):
        """
        Returns the filters which have an actual value, this allows us too
        make certain filters not required in the form, but when its empty it
        wont affect the filters.
        """

        if not self.form.is_valid():
            return {}

        filters = {}

        for name, value in self.form.cleaned_data.iteritems():
            if value or value == 0:
                filters[name] = value

        return self.clean_filters(filters)

    def clean_filters(self, filters):
        return filters

    def has_filters(self):

        if not self.filter_form_class:
            return False

        return any(key in self.form.fields for key in self.form.data.keys())

    @cached_property
    def form(self):
        """
        Make sure the form is only initialized once, thus we cache the form as
        soon as its initialized.
        """
        return self.get_form(self.get_form_class())

    def get_form_class(self):
        return self.filter_form_class

    @cached_property
    def filters(self):
        """
        Make the final filters available as a property on self after validating
        the form once.
        """
        return self.get_filters()


class OrderByMixin(object):

    ORDER_DESC = '-'
    ORDER_ASC = ''

    order_by_parameter_name = 'order_by'

    def get_context_data(self, **kwargs):

        order_by = self.get_order_by()

        if order_by and hasattr(self, 'object_list') and callable(getattr(self.object_list, 'order_by', None)):
            self.object_list = self.get_ordered(self.object_list, order_by)

        return super(OrderByMixin, self).get_context_data(**kwargs)

    def get_default_order_by(self):
        return self.order_by

    def get_order_by(self):
        if self.order_by_parameter_name in self.request.GET:
            return self.request.GET[self.order_by_parameter_name]

    def get_direction(self, order_by):

        # Base on first character (if it equals ORDER_DESC) which direction the sort will be
        return self.ORDER_DESC if order_by.startswith(self.ORDER_DESC) else self.ORDER_ASC

    def get_field_name(self, order_by):

        # When ordering descending, strip first character (E.g. -name would be name)
        return order_by[1:] if order_by.startswith(self.ORDER_DESC) else order_by

    def get_ordered(self, object_list, order_by):

        direction = self.get_direction(order_by)
        column_name = self.get_field_name(order_by)

        # Check if column is a part of table configuration
        column = self.get_table_class()[column_name]

        # Is column sortable?
        if not column or not column.sortable:
            return object_list

        # Convert table configuration field name to order_by_column if defined
        order_by = '{}{}'.format(direction, column.order_by_column or column_name)

        return object_list.order_by(order_by)


class PaginationMixin(object):

    paginator_class = DiggPaginator

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page,
                                    body=10, padding=2, margin=2, tail=3)
