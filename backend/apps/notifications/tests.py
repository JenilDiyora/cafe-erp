"""Unit tests for notification and email dispatch services."""
from datetime import date, time
from decimal import Decimal
from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User

from apps.notifications.emails import (
    send_cafe_email,
    send_otp_email,
    send_order_confirmation_email,
    send_reservation_confirmation_email,
    send_reservation_cancellation_email
)
from apps.tables.models import CafeTable
from apps.menu.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.reservations.models import TableReservation


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NotificationEmailsTestCase(TestCase):
    """Verify that email templates render and dispatch without errors."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer@example.com',
            email='testcustomer@example.com',
            first_name='Test',
            last_name='User',
            password='Password@123'
        )
        self.category = Category.objects.create(name='Coffee', slug='coffee', display_order=1)
        self.product = Product.objects.create(
            name='Americano',
            slug='americano',
            category=self.category,
            price=Decimal('150.00'),
            is_available=True
        )
        self.table = CafeTable.objects.create(
            table_number='Table 01',
            capacity=2,
            location='Window Side'
        )

    def test_send_cafe_email(self):
        res = send_cafe_email("Test Subject", "<p>Hello World</p>", ["recipient@example.com"])
        self.assertTrue(res)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        self.assertEqual(mail.outbox[0].to, ["recipient@example.com"])

    def test_send_otp_email(self):
        res = send_otp_email("recipient@example.com", "654321", purpose="Account Verification")
        self.assertTrue(res)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("654321", mail.outbox[0].subject)
        self.assertIn("654321", mail.outbox[0].body)

    def test_send_order_confirmation_email(self):
        order = Order.objects.create(
            customer=self.user,
            customer_name="Test User",
            customer_email="testcustomer@example.com",
            customer_phone="9876543210",
            table=self.table,
            order_type='DINE_IN',
            subtotal=Decimal('150.00'),
            tax=Decimal('7.50'),
            total=Decimal('157.50')
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name="Americano",
            unit_price=Decimal('150.00'),
            quantity=1,
            subtotal=Decimal('150.00')
        )
        res = send_order_confirmation_email(order)
        self.assertTrue(res)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(order.order_number, mail.outbox[0].subject)

    def test_send_reservation_confirmation_email(self):
        resv = TableReservation.objects.create(
            customer=self.user,
            customer_name="Test User",
            customer_email="testcustomer@example.com",
            customer_phone="9876543210",
            table=self.table,
            reservation_date=date.today(),
            start_time=time(18, 0),
            end_time=time(19, 30),
            guest_count=2
        )
        res = send_reservation_confirmation_email(resv)
        self.assertTrue(res)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(resv.reservation_number, mail.outbox[0].subject)

    def test_send_reservation_cancellation_email(self):
        resv = TableReservation.objects.create(
            customer=self.user,
            customer_name="Test User",
            customer_email="testcustomer@example.com",
            customer_phone="9876543210",
            table=self.table,
            reservation_date=date.today(),
            start_time=time(18, 0),
            end_time=time(19, 30),
            guest_count=2,
            status='CANCELLED'
        )
        res = send_reservation_cancellation_email(resv)
        self.assertTrue(res)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Cancelled", mail.outbox[0].subject)

