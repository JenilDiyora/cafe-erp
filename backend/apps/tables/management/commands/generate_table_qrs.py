"""Management command to generate or refresh QR codes for cafe tables."""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.tables.models import CafeTable


class Command(BaseCommand):
    help = "Generate or refresh high-resolution QR codes for physical cafe tables"

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            type=str,
            default='',
            help="Base URL for QR codes (e.g., 'https://cafe-erp.onrender.com' or 'http://127.0.0.1:8000'). Defaults to settings.SITE_URL."
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help="Regenerate QR images even if an image already exists."
        )
        parser.add_argument(
            '--table',
            type=str,
            default='',
            help="Generate only for a specific table number (e.g. 'Table 01')."
        )

    def handle(self, *args, **options):
        base_url = options['base_url'].strip() or getattr(settings, 'SITE_URL', 'https://cafe-erp.onrender.com')
        base_url = base_url.rstrip('/')
        force = options['force']
        target_table = options['table'].strip()

        qs = CafeTable.objects.all().order_by('table_number')
        if target_table:
            qs = qs.filter(table_number__iexact=target_table)
            if not qs.exists():
                self.stdout.write(self.style.ERROR(f"Table '{target_table}' not found in database."))
                return

        self.stdout.write(self.style.NOTICE(f"Base Domain for QR codes: {base_url}"))
        self.stdout.write("Generating QR codes...")

        count = 0
        for table in qs:
            if not table.qr_image or force:
                table.generate_qr_code(base_url=base_url)
                count += 1
                qr_url = f"{base_url}/table/{table.qr_token}/"
                self.stdout.write(
                    self.style.SUCCESS(f"  [OK] {table.table_number:10} -> {qr_url} (Image: {table.qr_image.name})")
                )
            else:
                self.stdout.write(
                    f"  [SKIP] {table.table_number:10} (QR image already exists. Use --force to overwrite)"
                )

        self.stdout.write(self.style.SUCCESS(f"Done! Generated QR codes for {count} table(s)."))
