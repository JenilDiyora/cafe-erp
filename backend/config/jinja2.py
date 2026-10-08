"""Jinja2 environment configuration for Django."""
from jinja2 import Environment
from django.urls import reverse
from django.templatetags.static import static
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from django.contrib.messages import get_messages


def csrf_input(request):
    """Generate CSRF hidden input field for forms."""
    if not request:
        return mark_safe('')
    token = get_token(request)
    return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')


def get_active_cafe_settings():
    """Retrieve the active cafe settings singleton or default."""
    try:
        from apps.core.models import CafeSetting
        return CafeSetting.objects.filter(is_active=True).first()
    except Exception:
        return None


def get_opening_hours_list():
    """Retrieve opening hours ordered by display_order."""
    try:
        from apps.core.models import OpeningHour
        return OpeningHour.objects.all().order_by('display_order', 'id')
    except Exception:
        return []


def format_currency(value):
    """Format decimal/float as Indian Rupee or standard currency."""
    if value is None:
        return "₹0.00"
    try:
        return f"₹{float(value):,.2f}".rstrip('0').rstrip('.') if float(value).is_integer() else f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"


def environment(**options):
    """Initialize and configure the Jinja2 Environment."""
    env = Environment(**options)

    # Globals available in all Jinja2 templates
    env.globals.update({
        'static': static,
        'url': reverse,
        'get_messages': get_messages,
        'get_cafe_settings': get_active_cafe_settings,
        'get_opening_hours': get_opening_hours_list,
        'range': range,
        'len': len,
        'min': min,
        'max': max,
    })

    # Filters
    env.filters.update({
        'currency': format_currency,
    })

    return env
