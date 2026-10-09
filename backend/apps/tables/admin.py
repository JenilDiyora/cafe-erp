"""Admin interface for Cafe Tables with live QR previews and generation actions."""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CafeTable


@admin.register(CafeTable)
class CafeTableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'table_name', 'capacity', 'location', 'is_active', 'qr_preview', 'qr_actions')
    list_filter = ('location', 'is_active', 'capacity')
    search_fields = ('table_number', 'table_name', 'qr_token')
    readonly_fields = ('qr_token', 'qr_preview_large', 'created_at', 'updated_at')
    actions = ['generate_qr_codes', 'activate_tables', 'deactivate_tables']

    fieldsets = (
        ('Table Information', {
            'fields': ('table_number', 'table_name', 'capacity', 'location', 'is_active')
        }),
        ('QR Ordering Details', {
            'fields': ('qr_token', 'qr_image', 'qr_preview_large')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def qr_preview(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" style="width: 44px; height: 44px; border-radius: 6px; border: 1px solid #ddd;" />', obj.qr_image.url)
        return "Not Generated"
    qr_preview.short_description = "QR Preview"

    def qr_preview_large(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" style="max-width: 200px; border-radius: 12px; border: 2px solid #ddd;" />', obj.qr_image.url)
        return "Save or trigger generation to create QR code."
    qr_preview_large.short_description = "Large QR"

    def qr_actions(self, obj):
        print_url = reverse('tables:qr_print', kwargs={'table_id': obj.id})
        download_btn = ""
        if obj.qr_image:
            download_btn = f'<a class="button" href="{obj.qr_image.url}" download style="margin-left: 6px; padding: 4px 8px; font-size: 11px;">⬇ Download</a>'
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 4px 8px; font-size: 11px;">🖨 Print Stand</a>{}',
            print_url,
            format_html(download_btn)
        )
    qr_actions.short_description = "QR Actions"

    @admin.action(description="Generate / Refresh QR codes for selected tables")
    def generate_qr_codes(self, request, queryset):
        base_url = request.build_absolute_uri('/')
        count = 0
        for table in queryset:
            table.generate_qr_code(base_url=base_url)
            count += 1
        self.message_user(request, f"Successfully generated QR codes for {count} table(s).")

    @admin.action(description="Activate selected tables")
    def activate_tables(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} table(s) activated.")

    @admin.action(description="Deactivate selected tables")
    def deactivate_tables(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} table(s) deactivated.")

