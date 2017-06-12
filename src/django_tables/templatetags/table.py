import copy

from django import template


register = template.Library()


@register.inclusion_tag('django_tables/table.html', takes_context=True)
def render_table(context, table):

    # Add the table to this new context, while copying it before that to prevent
    # messing with the global context
    context = copy.copy(context)
    context['table'] = table

    return context


@register.simple_tag(takes_context=True)
def render_cell(context, cell):
    return cell.render(context)
