"""CafeTable model with secure QR token generation and QR image handling."""
import secrets
from io import BytesIO
from django.db import models
from django.core.files import File
from django.urls import reverse
import qrcode
from PIL import Image


class CafeTable(models.Model):
    """Cafe physical dining table with unique QR code for in-store ordering."""
    LOCATION_CHOICES = [
        ('Main Hall', 'Main Hall'),
        ('Window Side', 'Window Side'),
        ('Terrace Garden', 'Terrace Garden'),
        ('Private Lounge', 'Private Lounge'),
        ('Outdoor Patio', 'Outdoor Patio'),
    ]

    table_number = models.CharField(max_length=20, unique=True, help_text="e.g., '01', 'Table 05'")
    table_name = models.CharField(max_length=100, blank=True, help_text="Descriptive name, e.g., 'Corner Garden Booth'")
    qr_token = models.CharField(max_length=64, unique=True, db_index=True, blank=True)
    capacity = models.PositiveIntegerField(default=4, help_text="Number of seats")
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, default='Main Hall')
    is_active = models.BooleanField(default=True, help_text="Active tables are available for QR ordering and reservations")
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="Generated QR code image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cafe Table"
        verbose_name_plural = "Cafe Tables"
        ordering = ['table_number']

    def __str__(self):
        name_str = f" - {self.table_name}" if self.table_name else ""
        return f"{self.table_number}{name_str} ({self.location}, Seats {self.capacity})"

    def save(self, *args, **kwargs):
        # Generate cryptographically secure random token if missing
        if not self.qr_token:
            self.qr_token = secrets.token_urlsafe(24)
        super().save(*args, **kwargs)
        # Auto-generate QR code image if not yet created
        if not self.qr_image:
            self.generate_qr_code()

    def get_absolute_url(self):
        return reverse('tables:table_entry', kwargs={'qr_token': self.qr_token})

    def generate_qr_code(self, base_url=None):
        """Generate high-resolution QR image pointing to table URL and save to model."""
        if not base_url:
            from django.conf import settings
            base_url = getattr(settings, 'SITE_URL', '')
            if not base_url:
                base_url = 'https://cafe-erp.onrender.com' if not getattr(settings, 'DEBUG', True) else 'http://127.0.0.1:8000'

        target_url = f"{base_url.rstrip('/')}/table/{self.qr_token}/"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=3,
        )
        qr.add_data(target_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#2d1810", back_color="#ffffff").convert('RGB')

        # Save with stable filename to avoid git file deletion / hash suffix churn
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        rel_path = f"qr_codes/table_{self.table_number.replace(' ', '_').lower()}.png"
        if default_storage.exists(rel_path):
            default_storage.delete(rel_path)

        saved_name = default_storage.save(rel_path, ContentFile(buffer.getvalue()))
        self.qr_image.name = saved_name
        self.save(update_fields=['qr_image', 'updated_at'])

