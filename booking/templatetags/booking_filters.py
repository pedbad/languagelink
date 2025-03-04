from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """ Retrieves an item from a dictionary safely in Django templates. """
    return dictionary.get(key, {})
