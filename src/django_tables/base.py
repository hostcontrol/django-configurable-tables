from __future__ import unicode_literals

import copy

from django.template import TemplateDoesNotExist
from django.template.loader import find_template, render_to_string
from django.utils.translation import gettext_lazy as _

import six

from django_tables.column import Column


DEFAULT_NAMES = ('empty_message', 'template_directory', 'default_columns', 'context_name')


_table_registry = {}


def get_tables():
    """
    Returns all tables registered
    """
    return _table_registry


class Options(object):

    def __init__(self, meta):
        self.columns = []
        self.meta = meta

        self.empty_message = _('No results matching your current filters')
        self.template_directory = None
        self.default_columns = None
        self.context_name = None

    def contribute_to_class(self, cls, name):

        cls._meta = self

        if self.meta:

            meta_attrs = self.meta.__dict__.copy()

            for name in self.meta.__dict__:
                # Ignore any private attributes that we don't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]

            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))

                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))


class TableBase(type):

    def __new__(mcs, name, bases, attrs):
        """
        This metaclass adds a declarative style of action-configurations to the product configuration class.

        Inspired by :class:`django.forms.form.DeclarativeFieldsMetaclass`
        """

        # First add all columns declared on the current class
        current_columns = {}
        for key, value in attrs.items():
            if isinstance(value, Column):
                column = attrs.pop(key)
                column.set_column_name(name=key)
                current_columns[key] = column

        attrs['declared_columns'] = current_columns
        new_class = type.__new__(mcs, name, bases, attrs)

        # Merge all columns declared on extending classes.
        # Walk through MRO and add columns declared on base classes. The MRO is walked in reverse order starting with
        # "object" ends with classes extending Table.
        declared_columns = {}
        for base in reversed(new_class.__mro__):
            if hasattr(base, 'declared_columns'):
                declared_columns.update(base.declared_columns)

            # Column shadowing. i.e. remove column if set to None in overriding class.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_columns:
                    declared_columns.pop(attr)

        meta = attrs.pop('Meta', None)  # Get meta from current class

        if not meta:
            # Get meta class from parent class
            meta = getattr(new_class, 'Meta', None)

        Options(meta).contribute_to_class(new_class, '_meta')

        new_class._meta.columns = sorted(declared_columns.items(), key=lambda item: item[1].creation_counter)

        # Add the class to the registry so we can connect models and table classes
        if hasattr(meta, 'model'):
            _table_registry[meta.model] = new_class

        return new_class

    def __getitem__(self, item):
        for name, column in self._meta.columns:
            if name == item:
                return column


class Table(six.with_metaclass(TableBase)):

    def __init__(self, visible_columns, rows):
        self.visible_columns = visible_columns
        self.rows = rows

    def __iter__(self):
        for context in self.rows:
            yield Row(context, self)

    @property
    def columns(self):
        """
        Returns all visible columns.
        """

        for name, column in self._meta.columns:

            if name not in self.visible_columns and not column.is_always_visible:
                continue

            yield column

    @property
    def context_name(self):
        return self._meta.context_name

    @property
    def columns_count(self):
        """
        Gets count of visible columns in table(and wraps logic required to get
        it from generator)
        """

        return len(list(self.columns))


class Row(object):

    def __init__(self, context, table):
        self.table = table
        self.context = context

    def __iter__(self):
        for column in self.table.columns:
            yield Cell(self.context, column, self.table)


class Cell(object):

    def __init__(self, context, column, table):
        self.context = context
        self.column = column
        self.table = table

    def get_template_name(self):

        if self.column.template is not None:
            return self.column.template

        template_directory = 'bo_resellerarea/tables/{}'.format(self.table._meta.context_name)

        # In case the template directory is defined in the table we use that
        if self.table._meta.template_directory:
            template_directory = self.table._meta.template_directory

        template_name = '{}/{}.html'.format(template_directory, self.column.name)

        if self.column.template_name:
            template_name = '{}/{}'.format(template_directory, self.column.template_name)

        try:
            # Check if the template exists
            find_template(template_name)

        except TemplateDoesNotExist:
            return self.column.default_template

        return template_name

    def render(self, context_data):

        context_data = copy.copy(context_data)
        context_data.update({
            'object': self.context
        })

        try:
            context_data['value'] = self.column.get_value(self.context, self.column.name)

        except AttributeError:
            pass

        template_name = self.get_template_name()

        return render_to_string(template_name, context_data)
