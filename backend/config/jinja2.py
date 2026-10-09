"""Jinja2 environment configuration for Django with Phase 2 globals."""
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


def get_cart_count(request):
    """Retrieve the total quantity of items currently in customer's cart."""
    if not request:
        return 0
    try:
        from apps.cart.models import Cart
        cart = Cart.get_or_create_cart(request)
        return cart.get_item_count()
    except Exception:
        return 0


def get_table_context(request):
    """Retrieve table session context for dine-in badge and order flow."""
    if not request or not hasattr(request, 'session'):
        return None
    table_id = request.session.get('table_id')
    table_number = request.session.get('table_number')
    if table_id and table_number:
        return {
            'table_id': table_id,
            'table_number': table_number,
            'table_token': request.session.get('table_token'),
            'order_type': 'DINE_IN',
        }
    return None


def format_currency(value):
    """Format decimal/float as Indian Rupee or standard currency."""
    if value is None:
        return "₹0.00"
    try:
        val = float(value)
        return f"₹{val:,.2f}".rstrip('0').rstrip('.') if val.is_integer() else f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"


def is_smtp_configured():
    """Check if real SMTP credentials are configured."""
    from django.conf import settings
    return bool(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))


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
        'csrf_input': csrf_input,
        'csrf_field': csrf_input,
        'get_cart_count': get_cart_count,
        'get_table_context': get_table_context,
        'is_smtp_configured': is_smtp_configured,
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
