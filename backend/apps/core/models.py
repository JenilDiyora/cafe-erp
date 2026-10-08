from django.db import models


class CafeSetting(models.Model):
    """Cafe-wide configuration and metadata."""
    cafe_name = models.CharField(max_length=150, default="Mitra Cafe")
    tagline = models.CharField(max_length=255, default="Crafted Coffee, Delicious Bites & Warm Moments")
    logo = models.ImageField(upload_to='cafe/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='cafe/favicons/', blank=True, null=True)
    short_description = models.TextField(
        default="Your beloved neighborhood cafe offering handcrafted specialty coffees, freshly baked delicacies, and a warm, vibrant atmosphere."
    )
    about_description = models.TextField(
        default="Founded with a passion for soulful coffee and heartfelt hospitality, Mitra Cafe brings friends and families together over rich brews and authentic flavors."
    )
    phone = models.CharField(max_length=25, default="+91 7405401350")
    email = models.EmailField(default="jenildiyora760@gmail.com")
    address = models.CharField(max_length=255, default="Mitra Cafe, Chhaprabhatha, Surat, Gujarat 394520")
    google_maps_url = models.TextField(
        blank=True,
        default="https://maps.app.goo.gl/YjiYuT8wt5XhwfJC7"
    )
    instagram_url = models.URLField(blank=True, default="https://instagram.com")
    facebook_url = models.URLField(blank=True, default="https://facebook.com")
    whatsapp_number = models.CharField(max_length=25, blank=True, default="+917405401350")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cafe Setting"
        verbose_name_plural = "Cafe Settings"

    def __str__(self):
        return self.cafe_name


class OpeningHour(models.Model):
    """Daily opening and closing hours for the cafe."""
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    opening_time = models.CharField(max_length=30, default="08:00 AM")
    closing_time = models.CharField(max_length=30, default="10:00 PM")
    is_closed = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "Opening Hour"
        verbose_name_plural = "Opening Hours"

    def __str__(self):
        if self.is_closed:
            return f"{self.day}: Closed"
        return f"{self.day}: {self.opening_time} - {self.closing_time}"

