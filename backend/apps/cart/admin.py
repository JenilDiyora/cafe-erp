"""Admin interface for shopping carts."""
from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price', 'subtotal_display')

    def subtotal_display(self, obj):
        return f"₹{obj.subtotal}"
    subtotal_display.short_description = "Subtotal"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'session_key', 'items_count_display', 'total_display', 'updated_at')
    list_filter = ('updated_at', 'created_at')
    search_fields = ('customer__username', 'customer__email', 'session_key')
    inlines = [CartItemInline]

    def items_count_display(self, obj):
        return obj.get_item_count()
    items_count_display.short_description = "Total Items"

    def total_display(self, obj):
        return f"₹{obj.get_total()}"
    total_display.short_description = "Total Amount"

