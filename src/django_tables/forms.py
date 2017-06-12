from __future__ import unicode_literals, absolute_import

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class TableConfigurationForm(forms.Form):

    name = forms.CharField(max_length=255, widget=forms.HiddenInput())

    columns = forms.MultipleChoiceField(
        required=False,
        label=_('Columns'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox'}),
    )

    order_by = forms.ChoiceField(
        label=_('Default sorting'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    limit = forms.TypedChoiceField(
        label=_('Items per page'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=(
            (10, '10'),
            (20, '20'),
            (30, '30'),
            (40, '40'),
            (50, '50'),
            (100, '100'),
        ),
        coerce=int
    )

    def __init__(self, table_class, *args, **kwargs):

        super(TableConfigurationForm, self).__init__(*args, **kwargs)

        column_choices = []
        order_by_choices = []

        asc = lambda key: key
        desc = lambda key: '-{}'.format(key)

        for name, column in table_class._meta.columns:

            if column.is_always_visible:
                continue

            column_choices.append((name, column.label))

            if column.sortable:
                order_by_choices.append((asc(name), mark_safe('{} &#x21A7;'.format(unicode(column.label)))))
                order_by_choices.append((desc(name), mark_safe('{} &#x21A5;'.format(unicode(column.label)))))

        self.fields['columns'].choices = column_choices
        self.fields['order_by'].choices = order_by_choices
