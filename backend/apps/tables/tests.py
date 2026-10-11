import tempfile
from io import StringIO
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from apps.tables.models import CafeTable

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TableOrderingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_superuser(
            username='staff@mitracafe.com',
            email='staff@mitracafe.com',
            password='TestPassword123'
        )
        self.table = CafeTable.objects.create(
            table_number='Table 99',
            table_name='Test Window Table',
            capacity=4,
            location='Window Side',
            is_active=True
        )

    def test_table_creation_generates_token_and_qr(self):
        """Table creation should generate a secure token and QR code image."""
        self.assertTrue(bool(self.table.qr_token))
        self.assertTrue(bool(self.table.qr_image))

    def test_table_entry_sets_session(self):
        """Visiting /table/<token>/ should configure the session for Dine-in at the table."""
        url = reverse('tables:table_entry', kwargs={'qr_token': self.table.qr_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        self.assertEqual(session.get('table_id'), self.table.id)
        self.assertEqual(session.get('table_number'), self.table.table_number)
        self.assertEqual(session.get('order_type'), 'DINE_IN')

    def test_clear_table_session(self):
        """Customer can clear table session and switch back to takeaway."""
        # Enter table first
        self.client.get(reverse('tables:table_entry', kwargs={'qr_token': self.table.qr_token}))
        self.assertEqual(self.client.session.get('order_type'), 'DINE_IN')

        # Clear session
        response = self.client.get(reverse('tables:clear_session'))
        self.assertRedirects(response, reverse('menu:list'))
        self.assertIsNone(self.client.session.get('table_id'))
        self.assertEqual(self.client.session.get('order_type'), 'TAKEAWAY')

    def test_generate_table_qrs_management_command(self):
        """Management command should successfully generate QR codes with custom base URL."""
        out = StringIO()
        call_command('generate_table_qrs', '--base-url', 'https://cafe-erp.onrender.com', '--force', stdout=out)
        output = out.getvalue()
        self.assertIn('https://cafe-erp.onrender.com', output)
        self.assertIn('Table 99', output)

    def test_admin_qr_print_all_view(self):
        """Staff should be able to view the printable sheet of all table QR stands."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('tables:qr_print_all'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Table 99')
