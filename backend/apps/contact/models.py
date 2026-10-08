from django.db import models


class ContactInquiry(models.Model):
    """Customer inquiry submitted through the contact form."""
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=25, blank=True)
    subject = models.CharField(max_length=200, blank=True, default="General Inquiry")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} - {self.subject or 'Inquiry'} ({self.created_at.strftime('%Y-%m-%d')})"

