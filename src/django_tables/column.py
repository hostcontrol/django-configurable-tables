from __future__ import unicode_literals, absolute_import


class Column(object):

    creation_counter = 0
    default_template = 'django_tables/columns/default.html'
    name = None

    def __init__(self, label=None, template=None, sortable=False, order_by_column=None, get_value_callback=None,
                 is_always_visible=False, template_name=None):

        # Increase the creation counter, and save our local copy, this is used
        # to keep track of the column order
        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

        self.label = label
        self.template = template
        self.sortable = sortable
        self.order_by_column = order_by_column
        self.get_value_callback = get_value_callback
        self.is_always_visible = is_always_visible
        self.template_name = template_name

    def set_column_name(self, name):

        self.name = name

        if self.label is None:
            self.label = name[0].upper() + name[1:].replace('_', ' ')

        if self.order_by_column is None and self.sortable:
            self.order_by_column = self.name

    def get_value(self, context, name):

        if self.get_value_callback:
            return self.get_value_callback(context, name)

        verbose_value_method = 'get_{}_display'.format(name)

        if hasattr(context, verbose_value_method):
            return getattr(context, verbose_value_method)()

        try:
            return getattr(context, name)

        except Exception:
            # Silently handle errors. Also fixes an issue with optional OneToOne relations where the relations does
            # not exist.
            pass

        if isinstance(context, dict):
            return context.get(name)


class DateColumn(Column):

    default_template = 'django_tables/columns/date.html'


class BooleanColumn(Column):

    default_template = 'django_tables/columns/boolean.html'


class TextColumn(Column):

    default_template = 'django_tables/columns/text.html'
