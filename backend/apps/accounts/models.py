"""Customer profile and OTP models for authentication."""
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomerProfile(models.Model):
    """Profile data extending Django standard User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, help_text="Customer contact phone number")
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.user.email})"


class EmailOTP(models.Model):
    """Secure One-Time Password for email verification and password reset."""
    PURPOSE_CHOICES = [
        ('REGISTER', 'Account Registration'),
        ('LOGIN', 'Account Login'),
        ('RESET_PASSWORD', 'Password Reset'),
        ('RESERVATION', 'Reservation Verification'),
    ]

    email = models.EmailField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='email_otps')
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='REGISTER')
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTP Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.email} [{self.purpose}] ({'Used' if self.is_used else 'Active'})"

    @classmethod
    def generate_otp(cls, email, user=None, purpose='REGISTER'):
        """Generate a cryptographically secure 6-digit OTP valid for 5 minutes."""
        code = str(secrets.randbelow(900000) + 100000)
        expires = timezone.now() + timedelta(minutes=5)

        # Invalidate previous un-used OTPs for this email & purpose
        cls.objects.filter(email=email, purpose=purpose, is_used=False).update(is_used=True)

        return cls.objects.create(
            email=email.strip().lower(),
            user=user,
            otp_code=code,
            purpose=purpose,
            expires_at=expires,
        )

    def is_valid(self):
        """Check if OTP is not used, within attempt limit, and not expired."""
        return (not self.is_used) and (self.attempts < 5) and (timezone.now() <= self.expires_at)

