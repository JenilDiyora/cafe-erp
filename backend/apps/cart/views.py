"""Views for shopping cart interactions with both AJAX and standard HTTP support."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from apps.menu.models import Product
from .models import Cart, CartItem


class CartDetailView(View):
    """View customer cart with live items, recalculation, and checkout button."""

    def get(self, request):
        cart = Cart.get_or_create_cart(request)
        cart_items = cart.items.select_related('product', 'product__category').all()

        context = {
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': cart.get_subtotal(),
            'tax': cart.get_tax(),
            'total': cart.get_total(),
            'table_number': request.session.get('table_number'),
            'order_type': request.session.get('order_type', 'TAKEAWAY'),
            'page_title': 'Your Cart',
        }
        return render(request, 'cart/cart.html', context)


class AddToCartView(View):
    """Add a menu item to the cart or increment quantity."""

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        if not product.is_available:
            msg = f"Sorry, {product.name} is currently out of stock."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
            messages.warning(request, msg)
            return redirect('menu:list')

        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        cart = Cart.get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'unit_price': product.price}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.unit_price = product.price
            cart_item.save(update_fields=['quantity', 'unit_price'])

        success_msg = f"Added {quantity} × {product.name} to your cart."

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': success_msg,
                'cart_count': cart.get_item_count(),
                'item_quantity': cart_item.quantity,
                'subtotal': str(cart.get_subtotal()),
                'total': str(cart.get_total()),
            })

        messages.success(request, success_msg)
        return redirect(request.POST.get('next') or 'cart:detail')


class UpdateCartItemView(View):
    """Update item quantity (increase, decrease, or set exact value)."""

    def post(self, request, item_id):
        cart = Cart.get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        action = request.POST.get('action')
        new_quantity = item.quantity

        if action == 'increase':
            new_quantity += 1
        elif action == 'decrease':
            new_quantity -= 1
        elif 'quantity' in request.POST:
            try:
                new_quantity = int(request.POST['quantity'])
            except (ValueError, TypeError):
                pass

        if new_quantity <= 0:
            item.delete()
            item_deleted = True
            item_qty = 0
        else:
            item.quantity = new_quantity
            item.unit_price = item.product.price
            item.save(update_fields=['quantity', 'unit_price'])
            item_deleted = False
            item_qty = item.quantity

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'item_deleted': item_deleted,
                'item_quantity': item_qty,
                'item_subtotal': str(item.subtotal) if not item_deleted else "0.00",
                'cart_count': cart.get_item_count(),
                'subtotal': str(cart.get_subtotal()),
                'tax': str(cart.get_tax()),
                'total': str(cart.get_total()),
            })

        return redirect('cart:detail')


class RemoveCartItemView(View):
    """Remove product item entirely from cart."""

    def post(self, request, item_id):
        cart = Cart.get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        prod_name = item.product.name
        item.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f"Removed {prod_name} from your cart.",
                'cart_count': cart.get_item_count(),
                'subtotal': str(cart.get_subtotal()),
                'tax': str(cart.get_tax()),
                'total': str(cart.get_total()),
            })

        messages.info(request, f"Removed {prod_name} from cart.")
        return redirect('cart:detail')


class ClearCartView(View):
    """Empty all contents of cart."""

    def post(self, request):
        cart = Cart.get_or_create_cart(request)
        cart.clear()
        messages.info(request, "Your cart has been cleared.")
        return redirect('cart:detail')

