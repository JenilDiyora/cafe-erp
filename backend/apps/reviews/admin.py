from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'is_featured', 'is_active', 'display_order', 'created_at')
    list_editable = ('rating', 'is_featured', 'is_active', 'display_order')
    list_filter = ('rating', 'is_featured', 'is_active')
    search_fields = ('customer_name', 'review_text')
    ordering = ('display_order', '-created_at')

