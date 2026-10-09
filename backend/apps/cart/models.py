"""Shopping Cart and CartItem models with server-side pricing."""
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from apps.menu.models import Product


class Cart(models.Model):
    """Customer shopping cart supporting both authenticated users and guests."""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        ordering = ['-updated_at']

    def __str__(self):
        owner = self.customer.username if self.customer else f"Guest ({self.session_key[:8] if self.session_key else 'Anonymous'})"
        return f"Cart #{self.id} for {owner} ({self.get_item_count()} items)"

    @classmethod
    def get_or_create_cart(cls, request):
        """Retrieve existing cart or initialize a new one for current session or user."""
        if not request.session.session_key:
            request.session.save()

        if request.user.is_authenticated:
            # Check for existing user cart
            cart = cls.objects.filter(customer=request.user).order_by('-updated_at').first()
            if not cart:
                cart = cls.objects.create(customer=request.user)
            return cart
        else:
            session_key = request.session.session_key
            cart, _ = cls.objects.get_or_create(session_key=session_key, customer=None)
            return cart

    @classmethod
    def merge_guest_cart(cls, request, user):
        """When user logs in or registers, merge guest session cart into user's cart."""
        session_key = request.session.session_key
        if not session_key:
            return

        guest_cart = cls.objects.filter(session_key=session_key, customer=None).first()
        if not guest_cart or not guest_cart.items.exists():
            return

        user_cart, _ = cls.objects.get_or_create(customer=user)

        for guest_item in guest_cart.items.all():
            user_item = user_cart.items.filter(product=guest_item.product).first()
            if user_item:
                user_item.quantity += guest_item.quantity
                user_item.unit_price = guest_item.product.price  # Refresh price
                user_item.save()
            else:
                guest_item.cart = user_cart
                guest_item.unit_price = guest_item.product.price
                guest_item.save()

        guest_cart.delete()

    def get_subtotal(self):
        """Calculate total sum of cart items using fresh database product prices."""
        total = Decimal('0.00')
        for item in self.items.select_related('product').all():
            # Always recalculate from live product price
            total += Decimal(item.quantity) * Decimal(item.product.price)
        return total

    def get_tax(self):
        """Calculate 5% cafe GST."""
        return (self.get_subtotal() * Decimal('0.05')).quantize(Decimal('0.01'))

    def get_total(self):
        """Subtotal + Tax."""
        return self.get_subtotal() + self.get_tax()

    def get_item_count(self):
        """Total number of individual items in cart."""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Empty all items from cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """An individual product entry within a customer's cart."""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Server-verified price snapshot")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'product')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    @property
    def subtotal(self):
        return Decimal(self.quantity) * Decimal(self.product.price)

