from django.http.response import HttpResponseRedirect
from django.views.generic import ListView

from django_tables.mixins import TableMixin, FilterMixin, OrderByMixin, PaginationMixin


class ConfigurableTableView(TableMixin, FilterMixin, OrderByMixin, PaginationMixin, ListView):

    """
    Combines pagination, ordering, configurable columns and filtering into a
    single view.
    """

    paginate_by = 20

    def get_paginate_by(self, queryset):
        table_class = self.get_table_class()

        return self.get_table_configuration(table_class=table_class).limit

    def get_table_configuration(self, table_class):
        """
        Returns the initialized table configuration model for this table.
        """
        table_configuration, created = super(ConfigurableTableView, self).get_table_configuration(
            table_class=table_class
        )

        if created:
            table_configuration.limit = super(ConfigurableTableView, self).get_paginate_by(self.get_queryset())
            table_configuration.order_by = super(ConfigurableTableView, self).get_default_order_by()
            table_configuration.save(update_fields=['limit', 'order_by'])

        return table_configuration

    def get_context_data(self, **kwargs):
        context_data = super(ConfigurableTableView, self).get_context_data(**kwargs)

        table_class = self.get_table_class()
        table_name = self.get_table_name_for_table_class(table_class=table_class)
        table_configuration = self.get_table_configuration(table_class=table_class)
        table_configuration_form_class = self.get_table_configuration_form_class()
        table_configuration_form_initial = self.get_table_configuration_form_initial(
            table_configuration=table_configuration
        )
        table_configuration_form_kwargs = self.get_table_configuration_form_kwargs(
            table_class=table_class,
            initial=table_configuration_form_initial
        )
        table = self.get_table(
            table_class=table_class,
            columns=table_configuration.columns,
            queryset=context_data['object_list']
        )
        table_configuration_form = self.get_table_configuration_form(
            form_class=table_configuration_form_class,
            form_kwargs=table_configuration_form_kwargs
        )

        context_data.update({
            'table_name': table_name,
            'table': table,
            'table_configuration_form': table_configuration_form
        })

        return context_data

    def post(self, request, *args, **kwargs):

        table_class = self.get_table_class()
        table_configuration = self.get_table_configuration(table_class=table_class)

        table_configuration_form_class = self.get_table_configuration_form_class()
        table_configuration_form_initial = self.get_table_configuration_form_initial(
            table_configuration=table_configuration
        )
        table_configuration_form_kwargs = self.get_table_configuration_form_kwargs(
            table_class=table_class,
            initial=table_configuration_form_initial
        )

        form = self.get_table_configuration_form(
            form_class=table_configuration_form_class,
            form_kwargs=table_configuration_form_kwargs
        )

        # Copy the original QueryDict to make it mutable
        query_dict = request.GET.copy()

        if form.is_valid():

            table_configuration = self.get_table_configuration(table_class)

            # If the limit changed, remove the page parameter from the query string
            if 'limit' in form.cleaned_data and form.cleaned_data['limit'] != table_configuration.limit:
                if 'page' in query_dict:
                    del query_dict['page']

            for field, value in form.cleaned_data.items():
                setattr(table_configuration, field, value)

            keys = form.cleaned_data.keys()
            table_configuration.save(update_fields=keys)

        # Rebuild the URL (similar to request.get_full_path() but use the QueryDict object)
        redirect_to = '%s%s' % (request.path, ('?' + query_dict.urlencode()) if query_dict else '')

        return HttpResponseRedirect(redirect_to)
