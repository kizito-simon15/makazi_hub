from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

from django import template

register = template.Library()

@register.filter
def to_range(value):
    """
    Returns a range from 1 to the value (inclusive).
    """
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)

# in templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def startswith(value, arg):
    return value.startswith(arg)
