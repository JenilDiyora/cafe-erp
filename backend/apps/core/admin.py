from django.contrib import admin
from .models import CafeSetting, OpeningHour


@admin.register(CafeSetting)
class CafeSettingAdmin(admin.ModelAdmin):
    list_display = ('cafe_name', 'phone', 'email', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('cafe_name', 'email', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Branding & Info', {
            'fields': ('cafe_name', 'tagline', 'logo', 'favicon', 'short_description', 'about_description')
        }),
        ('Contact & Location', {
            'fields': ('phone', 'email', 'address', 'google_maps_url', 'whatsapp_number')
        }),
        ('Social Links', {
            'fields': ('instagram_url', 'facebook_url')
        }),
        ('Status & Timestamps', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('day', 'opening_time', 'closing_time', 'is_closed', 'display_order', 'is_active')
    list_editable = ('opening_time', 'closing_time', 'is_closed', 'display_order', 'is_active')
    list_filter = ('is_closed', 'is_active')
    ordering = ('display_order',)

