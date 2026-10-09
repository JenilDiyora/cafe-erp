"""Management command to test email and SMTP configuration for Mitra Cafe."""
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.notifications.emails import send_cafe_email


class Command(BaseCommand):
    help = "Test Django email dispatch and SMTP connection to jenildiyora760@gmail.com"

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipient',
            type=str,
            default='jenildiyora760@gmail.com',
            help='Recipient email address to send test message to'
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        backend = getattr(settings, 'EMAIL_BACKEND', 'Not set')
        host = getattr(settings, 'EMAIL_HOST', 'Not set')
        port = getattr(settings, 'EMAIL_PORT', 'Not set')
        user = getattr(settings, 'EMAIL_HOST_USER', 'Not set')
        pwd = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        tls = getattr(settings, 'EMAIL_USE_TLS', False)
        ssl_enabled = getattr(settings, 'EMAIL_USE_SSL', False)

        self.stdout.write("=" * 60)
        self.stdout.write("       Mitra Cafe - Email & SMTP Diagnostic Test       ")
        self.stdout.write("=" * 60)
        self.stdout.write(f"EMAIL_BACKEND     : {backend}")
        self.stdout.write(f"EMAIL_HOST        : {host}:{port}")
        self.stdout.write(f"EMAIL_USE_TLS     : {tls}")
        self.stdout.write(f"EMAIL_USE_SSL     : {ssl_enabled}")
        self.stdout.write(f"EMAIL_HOST_USER   : {user}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'[CONFIGURED]' if pwd else '[EMPTY / NOT CONFIGURED]'}")
        self.stdout.write(f"Target Recipient  : {recipient}")
        self.stdout.write("-" * 60)

        if not pwd and 'smtp' in backend.lower():
            self.stdout.write(self.style.WARNING(
                "WARNING: EMAIL_HOST_PASSWORD is empty. SMTP delivery to real inboxes will be rejected by Google.\n"
                "To fix: Generate a 16-character Google App Password and add EMAIL_HOST_PASSWORD to backend/.env."
            ))

        html_body = f"""
        <div style="font-family: Arial, sans-serif; padding: 24px; background: #fdfaf6; border-radius: 12px; border: 1px solid #e5a755;">
            <h2 style="color: #2d1810; margin-top: 0;">Mitra Cafe - SMTP Test Successful!</h2>
            <p style="color: #4a3b32; font-size: 15px;">
                Congratulations! If you are reading this email in your inbox, your Django SMTP setup is fully functional.
            </p>
            <div style="background: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #eeddd0; margin: 16px 0;">
                <p style="margin: 4px 0;"><strong>Sender:</strong> {user}</p>
                <p style="margin: 4px 0;"><strong>Recipient:</strong> {recipient}</p>
                <p style="margin: 4px 0;"><strong>SMTP Server:</strong> {host}:{port}</p>
            </div>
            <p style="color: #8c786c; font-size: 13px;">Mitra Cafe, Chhaprabhatha, Surat | +91 7405401350</p>
        </div>
        """

        self.stdout.write(f"Attempting to send test email to {recipient}...")
        success = send_cafe_email(
            subject="[Mitra Cafe] SMTP Delivery Test",
            html_content=html_body,
            recipient_list=[recipient]
        )

        if success:
            if 'smtp' in backend.lower():
                self.stdout.write(self.style.SUCCESS(
                    f"\nSUCCESS! Real email transmitted over SMTP to {recipient}.\nPlease check your inbox and spam folder."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"\nSUCCESS (Console Backend): Email generated and printed to server console.\n"
                    f"To deliver directly to your real Gmail inbox, configure EMAIL_HOST_PASSWORD in backend/.env."
                ))
        else:
            self.stdout.write(self.style.ERROR(
                "\nFAILURE: Could not dispatch email. Please review the error log above."
            ))
        self.stdout.write("=" * 60)

