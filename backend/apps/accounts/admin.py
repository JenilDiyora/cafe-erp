"""Admin configuration for customer accounts and OTP logs."""
from django.contrib import admin
from .models import CustomerProfile, EmailOTP


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_address', 'phone', 'is_email_verified', 'created_at')
    list_filter = ('is_email_verified', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

    def email_address(self, obj):
        return obj.user.email
    email_address.short_description = "Email"


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'purpose', 'otp_code', 'is_used', 'attempts', 'expires_at', 'created_at')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('email', 'otp_code')
    readonly_fields = ('otp_code', 'created_at')
    ordering = ('-created_at',)

