"""Customer Orders and OrderItem models with price snapshots."""
import secrets
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from apps.menu.models import Product
from apps.tables.models import CafeTable


class Order(models.Model):
    """Customer order for Dine-in or Takeaway."""
    ORDER_TYPE_CHOICES = [
        ('DINE_IN', 'Dine-in'),
        ('TAKEAWAY', 'Takeaway'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Pickup / Serving'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='TAKEAWAY')
    table = models.ForeignKey(CafeTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="5% Cafe GST")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    notes = models.TextField(blank=True, help_text="Special preparation notes or dietary requests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name} ({self.get_order_type_display()}, ₹{self.total})"

    @classmethod
    def generate_order_number(cls):
        """Generate unique order identifier like ORD-1025."""
        last_order = cls.objects.all().order_by('-id').first()
        next_seq = (last_order.id + 1001) if last_order else 1001
        rand_suffix = secrets.randbelow(90) + 10
        order_num = f"ORD-{next_seq}"
        while cls.objects.filter(order_number=order_num).exists():
            next_seq += 1
            order_num = f"ORD-{next_seq}"
        return order_num


class OrderItem(models.Model):
    """Snapshot of a purchased product inside an order."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200, help_text="Historical name snapshot")
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Historical price snapshot")
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.product_name} × {self.quantity} (₹{self.subtotal})"

