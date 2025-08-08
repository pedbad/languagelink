# users/templatetags/form_utils.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def form_field(field, legend_text, placeholder=""):
    """
    Renders a full form-field block:
      <div class="form-field">…</div>
    Accepts an optional placeholder string.
    """
    help_id  = f"{field.id_for_label}_help"
    error_id = f"{field.id_for_label}_error"

    # Start building the attrs dict
    attrs = {
        "class":            "form-control",
        "aria-required":    str(field.field.required).lower(),
        "aria-invalid":     "true" if field.errors else "false",
        "aria-describedby": f"{help_id} {error_id}",
    }

    # If a placeholder was passed, include it
    if placeholder:
        attrs["placeholder"] = placeholder

    widget_html = field.as_widget(attrs=attrs)

    html = f"""
    <div class="form-field">
      <h3 class="form-heading">{legend_text}</h3>
      <div class="floating-input">
        <label for="{field.id_for_label}" class="sr-only">{legend_text}</label>
        {widget_html}
      </div>
      {f'<p id="{help_id}" class="mt-0.5 text-sm text-warm-brown">{field.help_text}</p>' if field.help_text else ''}
      {f'<p id="{error_id}" class="text-sm text-red-600">{field.errors}</p>'       if field.errors    else ''}
    </div>
    """
    return mark_safe(html)
