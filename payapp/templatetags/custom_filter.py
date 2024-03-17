from django import template
from decimal import Decimal
register = template.Library()

@register.filter
def subtract(value, arg):
    if isinstance(value, Decimal) and isinstance(arg, float):
        value = float(value)
    elif isinstance(value, float) and isinstance(arg, Decimal):
        arg = float(arg)
        
    return value - arg