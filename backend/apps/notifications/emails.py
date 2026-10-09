"""Email notification service for Mitra Cafe Phase 2."""
import sys
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Ensure stdout handles UTF-8 on Windows
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def send_cafe_email(subject, html_content, recipient_list):
    """Safe email sender with HTML and ASCII-clean plain-text fallback."""
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Mitra Cafe <jenildiyora760@gmail.com>')

    # Sanitize emojis for plaintext terminal compatibility on Windows cp1252
    text_content = strip_tags(html_content)
    clean_text = (
        text_content.replace('☕', '[Cafe]')
        .replace('⏱', '[Timer]')
        .replace('🎉', '[Success]')
        .replace('🪑', '[Table]')
        .encode('ascii', errors='replace')
        .decode('ascii')
    )
    clean_subject = (
        subject.replace('☕', '[Cafe]')
        .replace('🎉', '')
        .encode('ascii', errors='replace')
        .decode('ascii')
    )

    try:
        msg = EmailMultiAlternatives(
            subject=clean_subject,
            body=clean_text,
            from_email=from_email,
            to=recipient_list,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        backend_name = getattr(settings, 'EMAIL_BACKEND', '').split('.')[-1]
        logger.info(f"Email sent successfully to {recipient_list}: '{clean_subject}' via {backend_name}")
        if settings.DEBUG:
            print(f"📧 [EMAIL DISPATCHED via {backend_name}] To: {', '.join(recipient_list)} | Subject: {clean_subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list} ('{clean_subject}'): {e}")
        try:
            print("\n=======================================================")
            print(f"[EMAIL DISPATCH ISSUE] To: {', '.join(recipient_list)}")
            print(f"Subject: {clean_subject}")
            err_str = str(e)
            if "Authentication Required" in err_str or "Username and Password not accepted" in err_str or "535" in err_str or "530" in err_str or "Connection unexpectedly closed" in err_str:
                print(">> [GMAIL AUTHENTICATION REJECTED] Google rejected the credentials with 535 BadCredentials.")
                print(">> Most likely reason: The App Password was generated under a DIFFERENT Google account")
                print(">> in your browser (not jenildiyora760@gmail.com), or has a mistyped character.")
                print(">> Steps to fix:")
                print(">> 1. Open https://myaccount.google.com/apppasswords in an incognito window or ensure the active")
                print(">>    account in the top right is jenildiyora760@gmail.com.")
                print(">> 2. Generate a new 16-letter App Password named 'Mitra Cafe'.")
                print(">> 3. Paste it into backend/.env: EMAIL_HOST_PASSWORD=<16-letter-password>")
            print(f"Body Preview:\n{clean_text[:350]}")
            print("=======================================================\n")
        except Exception:
            pass
        return False


def send_otp_email(to_email, otp_code, purpose="Account Verification"):
    """Send 6-digit OTP with 5-minute expiry warning."""
    subject = f"Your Mitra Cafe Verification Code: {otp_code}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f7ede2; margin: 0; padding: 20px; }}
        .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #eeddd0; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
        .header {{ text-align: center; margin-bottom: 24px; }}
        .header h1 {{ color: #2d1810; margin: 0; font-size: 26px; }}
        .otp-box {{ background: #2d1810; color: #e5a755; font-size: 36px; font-weight: bold; letter-spacing: 8px; text-align: center; padding: 18px; border-radius: 12px; margin: 24px 0; }}
        .footer {{ text-align: center; font-size: 12px; color: #8c786c; margin-top: 30px; border-top: 1px solid #f0e4d8; padding-top: 15px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>Mitra Cafe</h1>
          <p style="color: #6d5b50; font-size: 14px;">{purpose}</p>
        </div>
        <p style="color: #4a3b32; font-size: 15px; line-height: 1.5;">
          Hello! Please use the following One-Time Password (OTP) to complete your {purpose.lower()}:
        </p>
        <div class="otp-box">{otp_code}</div>
        <p style="color: #c2410c; font-size: 13px; font-weight: 600; text-align: center;">
          This OTP is valid for 5 minutes only. Do not share this code with anyone.
        </p>
        <div class="footer">
          <p>Mitra Cafe, Chhaprabhatha, Surat, Gujarat 394520</p>
          <p>Contact: +91 7405401350 | jenildiyora760@gmail.com</p>
        </div>
      </div>
    </body>
    </html>
    """
    return send_cafe_email(subject, html_content, [to_email])


def send_order_confirmation_email(order):
    """Send order confirmation to customer."""
    subject = f"Order Confirmed #{order.order_number} - Mitra Cafe"

    table_info = f"Table {order.table.table_number}" if order.table else "Not Applicable (Takeaway)"
    items_rows = "".join([
        f"<tr><td style='padding: 8px 0; border-bottom: 1px solid #f0e4d8;'>{item.product_name} x {item.quantity}</td>"
        f"<td style='padding: 8px 0; border-bottom: 1px solid #f0e4d8; text-align: right;'>Rs {item.subtotal}</td></tr>"
        for item in order.items.all()
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f7ede2; margin: 0; padding: 20px; }}
        .card {{ max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #eeddd0; }}
        .header {{ text-align: center; border-bottom: 2px dashed #eeddd0; padding-bottom: 20px; margin-bottom: 20px; }}
        .pill {{ display: inline-block; padding: 6px 14px; background: #e5a755; color: #2d1810; font-weight: 700; border-radius: 50px; font-size: 13px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1 style="color: #2d1810; margin: 0;">Mitra Cafe</h1>
          <p style="color: #15803d; font-weight: bold; margin: 8px 0;">Order Successfully Placed</p>
          <span class="pill">Order #{order.order_number}</span>
        </div>
        <p><strong>Customer:</strong> {order.customer_name}</p>
        <p><strong>Order Type:</strong> {order.get_order_type_display()} ({table_info})</p>
        <p><strong>Status:</strong> {order.get_status_display()}</p>

        <table>
          <thead>
            <tr style="color: #6d5b50; text-align: left; font-size: 13px;">
              <th style="padding-bottom: 8px;">Item</th>
              <th style="padding-bottom: 8px; text-align: right;">Price</th>
            </tr>
          </thead>
          <tbody>
            {items_rows}
          </tbody>
          <tfoot>
            <tr>
              <td style="padding-top: 12px; font-weight: bold; font-size: 16px;">Total Amount:</td>
              <td style="padding-top: 12px; font-weight: bold; font-size: 16px; text-align: right; color: #c2410c;">Rs {order.total}</td>
            </tr>
          </tfoot>
        </table>

        {f"<p><strong>Notes:</strong> {order.notes}</p>" if order.notes else ""}

        <div style="text-align: center; margin-top: 30px; font-size: 12px; color: #8c786c;">
          <p>Thank you for dining with Mitra Cafe!</p>
          <p>Chhaprabhatha, Surat | +91 7405401350</p>
        </div>
      </div>
    </body>
    </html>
    """
    return send_cafe_email(subject, html_content, [order.customer_email])


def send_reservation_confirmation_email(reservation):
    """Send table reservation confirmation email."""
    subject = f"Table Reservation Confirmed #{reservation.reservation_number} - Mitra Cafe"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f7ede2; margin: 0; padding: 20px; }}
        .card {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #eeddd0; }}
        .header {{ text-align: center; border-bottom: 2px dashed #eeddd0; padding-bottom: 16px; margin-bottom: 20px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1 style="color: #2d1810; margin: 0;">Mitra Cafe</h1>
          <p style="color: #15803d; font-weight: bold; margin: 6px 0;">Table Reservation Confirmed</p>
          <p style="color: #6d5b50; font-size: 14px;">Ref #{reservation.reservation_number}</p>
        </div>
        <p>Dear <strong>{reservation.customer_name}</strong>,</p>
        <p>Your table reservation at Mitra Cafe has been confirmed with the following details:</p>
        <ul style="line-height: 1.8; color: #4a3b32;">
          <li><strong>Date:</strong> {reservation.reservation_date.strftime('%A, %d %B %Y')}</li>
          <li><strong>Time:</strong> {reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}</li>
          <li><strong>Table:</strong> Table {reservation.table.table_number} ({reservation.table.location})</li>
          <li><strong>Guests:</strong> {reservation.guest_count} person(s)</li>
        </ul>
        {f"<p><strong>Special Request:</strong> {reservation.special_request}</p>" if reservation.special_request else ""}
        <p style="font-size: 13px; color: #8c786c; margin-top: 24px;">
          If you need to reschedule or cancel, you can do so from your customer account page.
        </p>
      </div>
    </body>
    </html>
    """
    return send_cafe_email(subject, html_content, [reservation.customer_email])


def send_reservation_cancellation_email(reservation):
    """Send table reservation cancellation notice."""
    subject = f"Table Reservation Cancelled #{reservation.reservation_number}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #f7ede2; padding: 20px;">
      <div style="max-width: 520px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 12px;">
        <h2 style="color: #2d1810; margin-top: 0;">Mitra Cafe</h2>
        <p>Dear {reservation.customer_name},</p>
        <p>Your table reservation <strong>#{reservation.reservation_number}</strong> for {reservation.reservation_date.strftime('%d %B %Y')} has been cancelled.</p>
        <p>We hope to welcome you again soon!</p>
      </div>
    </body>
    </html>
    """
    return send_cafe_email(subject, html_content, [reservation.customer_email])

