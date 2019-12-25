from django import template

register = template.Library()


def memory_limit(value):
    """Removes all values of arg from the given string"""
    if value < 80000:
        return f"{value} KB"
    else:
        return f"{value // 1024} MB"


def time_limit(value):
    if value < 1000:
        return f"{value} ms"
    else:
        return f"{(value / 1000.):.2f} seconds"


register.filter('memory_limit', memory_limit)
register.filter('time_limit', time_limit)
