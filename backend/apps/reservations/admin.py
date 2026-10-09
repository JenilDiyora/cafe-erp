"""Admin interface for Table Reservations."""
from django.contrib import admin
from .models import TableReservation


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = (
        'reservation_number',
        'customer_name',
        'customer_phone',
        'table',
        'reservation_date',
        'start_time',
        'end_time',
        'guest_count',
        'status',
        'created_at'
    )
    list_filter = ('status', 'reservation_date', 'table', 'guest_count')
    search_fields = (
        'reservation_number',
        'customer_name',
        'customer_email',
        'customer_phone',
        'table__table_number'
    )
    readonly_fields = ('reservation_number', 'created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled', 'mark_noshow']

    @admin.action(description="Mark selected as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
        self.message_user(request, "Selected reservations confirmed.")

    @admin.action(description="Mark selected as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
        self.message_user(request, "Selected reservations marked as Completed.")

    @admin.action(description="Mark selected as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, "Selected reservations marked as Cancelled.")

    @admin.action(description="Mark selected as No-Show")
    def mark_noshow(self, request, queryset):
        queryset.update(status='NO_SHOW')
        self.message_user(request, "Selected reservations marked as No-Show.")

