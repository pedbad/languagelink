# users/templatetags/form_utils.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def form_field(field, legend_text, placeholder="", **extra_attrs):
    """
    Renders a full form-field block:
      <div class="form-field">…</div>
    Automatically:
     - Adds HTML5 `required` to required fields
     - Appends “(Optional)” to the legend_text for non-required fields
     - Manages aria-required, aria-invalid, aria-describedby
    """
    help_id  = f"{field.id_for_label}_help"
    error_id = f"{field.id_for_label}_error"

    # Build base attrs from field metadata
    attrs = {
        "class":        "form-control",
        "aria-required": str(field.field.required).lower(),
        "aria-invalid":  "true" if field.errors else "false",
    }

    # HTML5 required attribute
    if field.field.required:
        attrs["required"] = "required"
    else:
        # append “(Optional)” to the heading
        legend_text = f"{legend_text} <span class='text-sm text-gray-500'>(Optional)</span>"

    # Placeholder if provided
    if placeholder:
        attrs["placeholder"] = placeholder

    # Build aria-describedby if help or errors exist
    desc = []
    if field.help_text:
        desc.append(help_id)
    if field.errors:
        desc.append(error_id)
    if desc:
        attrs["aria-describedby"] = " ".join(desc)

    # Merge any extra_attrs the caller passed
    attrs.update(extra_attrs)

    # Render the widget
    widget_html = field.as_widget(attrs=attrs)

    # Finally, assemble the full block
    html = f"""
    <div class="form-field">
      <h3 class="form-heading">{legend_text}</h3>
      <div class="floating-input">
        <label for="{field.id_for_label}" class="sr-only">{field.label}</label>
        {widget_html}
      </div>
      {f'<p id="{help_id}" class="mt-0.5 text-sm text-warm-brown">{field.help_text}</p>' if field.help_text else ''}
      {f'<p id="{error_id}" class="text-sm text-red-600">{field.errors}</p>'       if field.errors    else ''}
    </div>
    """
    return mark_safe(html)
