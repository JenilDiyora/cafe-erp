"""Seed initial tables, QR codes, sample customer, orders, and reservations for Phase 2."""
from datetime import date, time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tables.models import CafeTable
from apps.accounts.models import CustomerProfile
from apps.menu.models import Product
from apps.orders.models import Order, OrderItem
from apps.reservations.models import TableReservation

User = get_user_model()


class Command(BaseCommand):
    help = "Seed tables, QR codes, sample customer, orders and reservations for Phase 2"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Phase 2 cafe tables and customer data...")

        # 1. Create Tables
        tables_data = [
            {'num': 'Table 01', 'name': 'Espresso Corner', 'cap': 2, 'loc': 'Window Side'},
            {'num': 'Table 02', 'name': 'Sunshine Booth', 'cap': 2, 'loc': 'Window Side'},
            {'num': 'Table 03', 'name': 'Central Lounge', 'cap': 4, 'loc': 'Main Hall'},
            {'num': 'Table 04', 'name': 'Artisan Table', 'cap': 4, 'loc': 'Main Hall'},
            {'num': 'Table 05', 'name': 'Terrace Breeze', 'cap': 4, 'loc': 'Terrace Garden'},
            {'num': 'Table 06', 'name': 'Garden Canopy', 'cap': 6, 'loc': 'Terrace Garden'},
            {'num': 'Table 07', 'name': 'VIP Family Room', 'cap': 8, 'loc': 'Private Lounge'},
            {'num': 'Table 08', 'name': 'Patio Umbrella', 'cap': 4, 'loc': 'Outdoor Patio'},
        ]

        created_tables = []
        for t_info in tables_data:
            table, created = CafeTable.objects.get_or_create(
                table_number=t_info['num'],
                defaults={
                    'table_name': t_info['name'],
                    'capacity': t_info['cap'],
                    'location': t_info['loc'],
                    'is_active': True,
                }
            )
            # Generate QR code if missing
            if not table.qr_image:
                table.generate_qr_code(base_url="http://127.0.0.1:8000")
            created_tables.append(table)
            self.stdout.write(f"  [OK] {table.table_number} ({table.location}, Seats {table.capacity}) [Token: {table.qr_token[:8]}...]")

        # 2. Sample Customer
        customer_email = "testcustomer@example.com"
        customer, c_created = User.objects.get_or_create(
            username=customer_email,
            defaults={
                'email': customer_email,
                'first_name': 'Aarav',
                'last_name': 'Patel',
                'is_active': True,
            }
        )
        if c_created:
            customer.set_password("Password@123")
            customer.save()
            CustomerProfile.objects.create(
                user=customer,
                phone="9876543210",
                is_email_verified=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Created customer '{customer_email}' (password: Password@123)"))
        else:
            profile, _ = CustomerProfile.objects.get_or_create(user=customer)
            profile.is_email_verified = True
            profile.save()

        # 3. Sample Orders
        prods = list(Product.objects.filter(is_available=True)[:4])
        if prods and not Order.objects.filter(customer=customer).exists():
            table_05 = CafeTable.objects.filter(table_number='Table 05').first()

            # Dine-in Order
            ord1 = Order.objects.create(
                order_number="ORD-1025",
                customer=customer,
                customer_name="Aarav Patel",
                customer_email=customer_email,
                customer_phone="9876543210",
                order_type="DINE_IN",
                table=table_05,
                status="PREPARING",
                notes="Extra hot cappuccino please",
            )
            OrderItem.objects.create(
                order=ord1,
                product=prods[0],
                product_name=prods[0].name,
                unit_price=prods[0].price,
                quantity=2,
                subtotal=prods[0].price * 2,
            )
            if len(prods) > 1:
                OrderItem.objects.create(
                    order=ord1,
                    product=prods[1],
                    product_name=prods[1].name,
                    unit_price=prods[1].price,
                    quantity=1,
                    subtotal=prods[1].price,
                )
            sub = sum(i.subtotal for i in ord1.items.all())
            tax = (sub * Decimal('0.05')).quantize(Decimal('0.01'))
            ord1.subtotal = sub
            ord1.tax = tax
            ord1.total = sub + tax
            ord1.save()

            # Takeaway Order
            ord2 = Order.objects.create(
                order_number="ORD-1024",
                customer=customer,
                customer_name="Aarav Patel",
                customer_email=customer_email,
                customer_phone="9876543210",
                order_type="TAKEAWAY",
                table=None,
                status="COMPLETED",
                notes="Pack securely for ride",
            )
            OrderItem.objects.create(
                order=ord2,
                product=prods[0],
                product_name=prods[0].name,
                unit_price=prods[0].price,
                quantity=1,
                subtotal=prods[0].price,
            )
            ord2.subtotal = prods[0].price
            ord2.tax = (prods[0].price * Decimal('0.05')).quantize(Decimal('0.01'))
            ord2.total = ord2.subtotal + ord2.tax
            ord2.save()

            self.stdout.write(self.style.SUCCESS("Created sample Dine-in & Takeaway orders"))

        # 4. Sample Reservation
        if not TableReservation.objects.filter(customer=customer).exists():
            tomorrow = date.today() + timedelta(days=1)
            t_res = CafeTable.objects.filter(table_number='Table 05').first()
            if t_res:
                TableReservation.objects.create(
                    reservation_number="RES-10025",
                    customer=customer,
                    customer_name="Aarav Patel",
                    customer_email=customer_email,
                    customer_phone="9876543210",
                    table=t_res,
                    reservation_date=tomorrow,
                    start_time=time(19, 30),
                    end_time=time(21, 0),
                    guest_count=4,
                    status="CONFIRMED",
                    special_request="Anniversary dinner, window corner preferred",
                )
                self.stdout.write(self.style.SUCCESS(f"Created sample table reservation for tomorrow at 07:30 PM"))

        self.stdout.write(self.style.SUCCESS("Phase 2 seed completed successfully!"))
