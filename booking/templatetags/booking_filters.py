from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
  """Safely get an item from a dictionary using a tuple key."""
  if isinstance(dictionary, dict):
    return dictionary.get(key, False)  # Default to False
  return False  # Prevent errors when `dictionary` isn't a dict
