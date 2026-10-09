"""Customer checkout, order creation, confirmation, and order history views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from apps.cart.models import Cart
from apps.tables.models import CafeTable
from apps.notifications.emails import send_order_confirmation_email
from .models import Order, OrderItem


@method_decorator(login_required(login_url='/account/login/?next=/checkout/'), name='dispatch')
class CheckoutView(View):
    """Checkout page displaying order review, table details, and order placement."""

    def get(self, request):
        cart = Cart.get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty. Please add items before checkout.")
            return redirect('menu:list')

        # Check for table context in session
        table = None
        table_id = request.session.get('table_id')
        if table_id:
            table = CafeTable.objects.filter(id=table_id, is_active=True).first()

        profile = getattr(request.user, 'profile', None)
        initial_name = request.user.get_full_name() or request.user.username
        initial_phone = profile.phone if profile else ''

        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all(),
            'subtotal': cart.get_subtotal(),
            'tax': cart.get_tax(),
            'total': cart.get_total(),
            'table': table,
            'default_order_type': 'DINE_IN' if table else 'TAKEAWAY',
            'customer_name': initial_name,
            'customer_email': request.user.email,
            'customer_phone': initial_phone,
            'page_title': 'Checkout Order',
        }
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = Cart.get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect('menu:list')

        # Collect customer fields
        name = request.POST.get('customer_name', '').strip() or request.user.get_full_name() or request.user.username
        email = request.POST.get('customer_email', '').strip() or request.user.email
        phone = request.POST.get('customer_phone', '').strip()
        notes = request.POST.get('notes', '').strip()

        # Update profile phone if not set
        if phone and hasattr(request.user, 'profile') and not request.user.profile.phone:
            request.user.profile.phone = phone
            request.user.profile.save(update_fields=['phone'])

        # Determine order type and table
        table_id = request.session.get('table_id')
        table = None
        if table_id:
            table = CafeTable.objects.filter(id=table_id, is_active=True).first()

        order_type_choice = request.POST.get('order_type', 'TAKEAWAY')
        if table:
            # Dine-in enforced if entered via QR table
            order_type = 'DINE_IN'
        else:
            order_type = 'TAKEAWAY'
            table = None

        # Calculate totals from fresh database prices
        subtotal = cart.get_subtotal()
        tax = cart.get_tax()
        total = cart.get_total()

        # Create Order
        order = Order.objects.create(
            order_number=Order.generate_order_number(),
            customer=request.user,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            order_type=order_type,
            table=table,
            status='PENDING',
            subtotal=subtotal,
            tax=tax,
            total=total,
            notes=notes,
        )

        # Snapshot cart items into OrderItem
        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )

        # Empty cart after successful placement
        cart.clear()

        # Send confirmation email
        send_order_confirmation_email(order)

        messages.success(request, f"Order #{order.order_number} has been placed successfully!")
        return redirect('orders:confirmation', order_number=order.order_number)


class OrderConfirmationView(View):
    """Post-checkout order confirmation and status summary."""

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)

        # Ownership security check
        if request.user.is_authenticated and not request.user.is_staff:
            if order.customer != request.user:
                raise PermissionDenied("You do not have permission to view this order.")

        context = {
            'order': order,
            'items': order.items.all(),
            'page_title': f'Order Confirmed - #{order.order_number}',
        }
        return render(request, 'orders/confirmation.html', context)


@method_decorator(login_required, name='dispatch')
class OrderHistoryView(View):
    """Customer account order history listing."""

    def get(self, request):
        orders = request.user.orders.all().order_by('-created_at')
        context = {
            'orders': orders,
            'page_title': 'My Order History',
        }
        return render(request, 'orders/orders.html', context)


@method_decorator(login_required, name='dispatch')
class OrderDetailView(View):
    """Customer view of a single order with live status timeline."""

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)

        # Ownership security check
        if order.customer != request.user and not request.user.is_staff:
            raise PermissionDenied("You do not have permission to view this order.")

        context = {
            'order': order,
            'items': order.items.all(),
            'page_title': f'Order #{order.order_number}',
        }
        return render(request, 'orders/order_detail.html', context)

