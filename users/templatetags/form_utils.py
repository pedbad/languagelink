# users/templatetags/form_utils.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def form_field(field, legend_text, placeholder="", **extra_attrs):
  """
  Renders a full form-field block:
    <div class="form-field">…</div>
  - Adds HTML5 `required` to required fields
  - Appends “(Optional)” to the legend for non-required fields
  - Manages aria-required, aria-invalid, aria-describedby
  """
  help_id = f"{field.id_for_label}_help"
  error_id = f"{field.id_for_label}_error"

  attrs = {
    "class": "form-control",
    "aria-required": str(field.field.required).lower(),
    "aria-invalid": "true" if field.errors else "false",
  }

  if field.field.required:
    attrs["required"] = "required"
  else:
    legend_text = (
      f"{legend_text} "
      "<span class='text-sm text-gray-500'>(Optional)</span>"
    )

  if placeholder:
    attrs["placeholder"] = placeholder

  desc_ids = []
  if field.help_text:
    desc_ids.append(help_id)
  if field.errors:
    desc_ids.append(error_id)
  if desc_ids:
    attrs["aria-describedby"] = " ".join(desc_ids)

  attrs.update(extra_attrs)
  widget_html = field.as_widget(attrs=attrs)

  html = f"""
  <div class="form-field">
    <h3 class="form-heading">{legend_text}</h3>
    <div class="floating-input">
      <label for="{field.id_for_label}" class="sr-only">{legend_text}</label>
      {widget_html}
    </div>
    {f'<p id="{help_id}" class="mt-0.5 text-sm text-warm-brown">{field.help_text}</p>' if field.help_text else ''}
    {f'<p id="{error_id}" class="text-sm text-red-600">{field.errors}</p>' if field.errors else ''}
  </div>
  """
  return mark_safe(html)


@register.filter
def add_input_classes(widget_html, css_classes):
  """
  Injects the given CSS classes into the first <input> tag in widget_html.
  """
  return mark_safe(widget_html.replace(
    '<input',
    f'<input class="{css_classes}"',
    1
  ))


@register.inclusion_tag("users/partials/radio_group.html")
def radio_group(group, legend_text, help_text=None, cols=2):
  """
  Renders a <fieldset> radio group for a RadioSelect bound field.
  - group        → the BoundField (e.g. form.university_status)
  - legend_text  → text for the <legend>
  - help_text    → optional helper text
  - cols         → number of columns on sm+ screens
  """
  help_id = f"{group.id_for_label}_help"
  error_id = f"{group.id_for_label}_error"

  desc_ids = []
  if help_text:
    desc_ids.append(help_id)
  if group.errors:
    desc_ids.append(error_id)
  described = " ".join(desc_ids)

  items = []
  for widget in group:
    raw = widget.tag()
    styled = raw.replace(
      "<input",
      '<input class="peer mr-4 h-5 w-5 text-primary-dark-teal '
      'border-gray-300 focus:ring-primary-dark-teal"',
      1
    )
    items.append({
      "input": mark_safe(styled),
      "label": widget.choice_label,
      "id": widget.id_for_label,
    })

  return {
    "items": items,
    "legend_text": legend_text,
    "help_text": help_text,
    "help_id": help_id,
    "error_id": error_id,
    "described": described,
    "is_required": group.field.required,
    "has_error": bool(group.errors),
    "cols": cols,
  }
