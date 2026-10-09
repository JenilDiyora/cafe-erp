"""Admin interface for managing customer orders and status updates."""
from django.contrib import admin
from apps.notifications.emails import send_cafe_email
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'unit_price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'order_type', 'table_display', 'status', 'total_display', 'created_at')
    list_filter = ('status', 'order_type', 'created_at', 'table')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'customer__username')
    readonly_fields = ('order_number', 'subtotal', 'tax', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_completed', 'mark_cancelled']

    def table_display(self, obj):
        return f"Table {obj.table.table_number}" if obj.table else "Takeaway"
    table_display.short_description = "Table"

    def total_display(self, obj):
        return f"₹{obj.total}"
    total_display.short_description = "Total"

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
        self.message_user(request, "Selected orders marked as Confirmed.")

    @admin.action(description="Mark selected orders as Preparing")
    def mark_preparing(self, request, queryset):
        queryset.update(status='PREPARING')
        self.message_user(request, "Selected orders marked as Preparing.")

    @admin.action(description="Mark selected orders as Ready")
    def mark_ready(self, request, queryset):
        queryset.update(status='READY')
        self.message_user(request, "Selected orders marked as Ready.")

    @admin.action(description="Mark selected orders as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
        self.message_user(request, "Selected orders marked as Completed.")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, "Selected orders marked as Cancelled.")

