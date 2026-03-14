from django import template

register = template.Library()

@register.filter
def intcomma(value):
    """
    Converts an integer to a string with commas every three digits.
    Example: 4500000000 becomes 4,500,000,000
    """
    try:
        value = int(float(value))
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value
