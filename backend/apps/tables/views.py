"""Views for table QR scanning, session initialization, and QR print/preview."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .models import CafeTable


class TableEntryView(View):
    """Entry point when customer scans physical table QR code: /table/<qr_token>/."""

    def get(self, request, qr_token):
        # 1 & 2: Validate token & find table
        try:
            table = CafeTable.objects.get(qr_token=qr_token)
        except CafeTable.DoesNotExist:
            return render(request, 'tables/table_landing.html', {
                'error_type': 'NOT_FOUND',
                'page_title': 'Table Not Found',
            }, status=404)

        # 3: Check if table is active
        if not table.is_active:
            return render(request, 'tables/table_landing.html', {
                'table': table,
                'error_type': 'INACTIVE',
                'page_title': 'Table Unavailable',
            }, status=403)

        # 4: Store table context securely in session
        request.session['table_id'] = table.id
        request.session['table_number'] = table.table_number
        request.session['table_token'] = table.qr_token
        request.session['order_type'] = 'DINE_IN'

        # 5: Check authentication
        if request.user.is_authenticated:
            messages.success(
                request,
                f"🪑 Seated at Table {table.table_number}! Add your favorites to the cart to place your dine-in order."
            )
            return redirect('menu:list')

        # If not authenticated, show welcoming table landing page with Login/Register/Browse options
        return render(request, 'tables/table_landing.html', {
            'table': table,
            'page_title': f'Seated at {table.table_number}',
        })


class ClearTableSessionView(View):
    """Allows customer to switch out of Dine-in mode back to normal takeaway browsing."""

    def get(self, request):
        request.session.pop('table_id', None)
        request.session.pop('table_number', None)
        request.session.pop('table_token', None)
        request.session['order_type'] = 'TAKEAWAY'
        messages.info(request, "Table session cleared. You are now browsing in Takeaway mode.")
        return redirect('menu:list')


@method_decorator(staff_member_required, name='dispatch')
class AdminQRPrintView(View):
    """Staff view to print a branded table tent QR stand for the table."""

    def get(self, request, table_id):
        table = get_object_or_404(CafeTable, id=table_id)

        # Generate QR if it doesn't exist yet
        if not table.qr_image:
            base_url = request.build_absolute_uri('/')
            table.generate_qr_code(base_url=base_url)

        return render(request, 'tables/qr_print.html', {
            'table': table,
            'page_title': f'Print QR Stand - {table.table_number}',
        })

