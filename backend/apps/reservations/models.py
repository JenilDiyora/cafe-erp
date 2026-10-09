"""Table Reservation model with double-booking prevention."""
import secrets
from datetime import datetime, timedelta, time
from django.db import models
from django.contrib.auth.models import User
from apps.tables.models import CafeTable


class TableReservation(models.Model):
    """Customer reservation for dining tables on specific future dates and times."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No-Show'),
    ]

    reservation_number = models.CharField(max_length=32, unique=True, db_index=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    table = models.ForeignKey(CafeTable, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    guest_count = models.PositiveIntegerField(default=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    special_request = models.TextField(blank=True, help_text="e.g. Birthday celebration, high chair, quiet corner")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Table Reservation"
        verbose_name_plural = "Table Reservations"
        ordering = ['-reservation_date', '-start_time']

    def __str__(self):
        return f"Reservation #{self.reservation_number} - {self.customer_name} ({self.table.table_number}, {self.reservation_date} {self.start_time})"

    @classmethod
    def generate_reservation_number(cls):
        """Generate unique reservation identifier like RES-10025."""
        last_res = cls.objects.all().order_by('-id').first()
        next_seq = (last_res.id + 10001) if last_res else 10001
        res_num = f"RES-{next_seq}"
        while cls.objects.filter(reservation_number=res_num).exists():
            next_seq += 1
            res_num = f"RES-{next_seq}"
        return res_num

    @classmethod
    def find_available_tables(cls, date_obj, start_time_obj, guest_count, duration_minutes=90):
        """Return list of active tables with sufficient capacity not booked during requested slot."""
        start_dt = datetime.combine(date_obj, start_time_obj)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time_obj = end_dt.time()

        # Filter active tables with sufficient capacity
        candidate_tables = CafeTable.objects.filter(is_active=True, capacity__gte=guest_count)

        # Find existing active reservations for this date
        conflicting_reservations = cls.objects.filter(
            reservation_date=date_obj,
            status__in=['PENDING', 'CONFIRMED'],
            start_time__lt=end_time_obj,
            end_time__gt=start_time_obj,
        ).values_list('table_id', flat=True)

        return candidate_tables.exclude(id__in=conflicting_reservations).order_by('capacity', 'table_number')

