"""Views for booking tables, checking availability, confirmation, and cancellation."""
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from apps.tables.models import CafeTable
from apps.notifications.emails import (
    send_reservation_confirmation_email,
    send_reservation_cancellation_email
)
from .models import TableReservation


class BookTableView(View):
    """Step 1: Check availability by date, time, and guest count."""

    def get(self, request):
        today_str = date.today().isoformat()
        selected_date_str = request.GET.get('date', today_str)
        selected_time_str = request.GET.get('time', '19:00')
        guests = int(request.GET.get('guests', 2))

        available_tables = None
        searched = False

        if 'date' in request.GET and 'time' in request.GET:
            try:
                date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                time_obj = datetime.strptime(selected_time_str, '%H:%M').time()

                # Don't allow past dates
                if date_obj < date.today():
                    messages.warning(request, "Please choose a future reservation date.")
                else:
                    available_tables = TableReservation.find_available_tables(
                        date_obj=date_obj,
                        start_time_obj=time_obj,
                        guest_count=guests,
                    )
                    searched = True
            except ValueError:
                messages.error(request, "Invalid date or time format.")

        context = {
            'selected_date': selected_date_str,
            'selected_time': selected_time_str,
            'guests': guests,
            'available_tables': available_tables,
            'searched': searched,
            'min_date': today_str,
            'page_title': 'Book a Table',
        }
        return render(request, 'reservations/book.html', context)

    def post(self, request):
        # Table selected from available list
        table_id = request.POST.get('table_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        guests = request.POST.get('guests', 2)

        if not table_id or not date_str or not time_str:
            messages.error(request, "Please select an available table to proceed.")
            return redirect('reservations:book')

        # Store in session draft
        request.session['reservation_draft'] = {
            'table_id': int(table_id),
            'date': date_str,
            'time': time_str,
            'guests': int(guests),
        }

        if not request.user.is_authenticated:
            messages.info(request, "Please log in or create an account to confirm your table reservation.")
            return redirect(f"/account/login/?next=/reservations/confirm/")

        return redirect('reservations:confirm')


@method_decorator(login_required(login_url='/account/login/?next=/reservations/confirm/'), name='dispatch')
class ConfirmReservationView(View):
    """Step 2: Review details, provide phone/special requests, and confirm booking."""

    def get(self, request):
        draft = request.session.get('reservation_draft')
        if not draft:
            messages.warning(request, "Please check availability and select a table first.")
            return redirect('reservations:book')

        table = get_object_or_404(CafeTable, id=draft['table_id'])
        date_obj = datetime.strptime(draft['date'], '%Y-%m-%d').date()
        time_obj = datetime.strptime(draft['time'], '%H:%M').time()
        end_time_obj = (datetime.combine(date_obj, time_obj) + timedelta(minutes=90)).time()

        profile = getattr(request.user, 'profile', None)

        context = {
            'table': table,
            'reservation_date': date_obj,
            'start_time': time_obj,
            'end_time': end_time_obj,
            'guests': draft['guests'],
            'customer_name': request.user.get_full_name() or request.user.username,
            'customer_email': request.user.email,
            'customer_phone': profile.phone if profile else '',
            'page_title': 'Confirm Table Reservation',
        }
        return render(request, 'reservations/confirmation.html', context)

    def post(self, request):
        draft = request.session.get('reservation_draft')
        if not draft:
            messages.error(request, "Reservation session expired. Please search again.")
            return redirect('reservations:book')

        table = get_object_or_404(CafeTable, id=draft['table_id'])
        date_obj = datetime.strptime(draft['date'], '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(draft['time'], '%H:%M').time()
        end_time_obj = (datetime.combine(date_obj, start_time_obj) + timedelta(minutes=90)).time()

        phone = request.POST.get('customer_phone', '').strip()
        special_request = request.POST.get('special_request', '').strip()

        # Update profile phone if not set
        if phone and hasattr(request.user, 'profile') and not request.user.profile.phone:
            request.user.profile.phone = phone
            request.user.profile.save(update_fields=['phone'])

        # Double-booking check right before saving!
        is_taken = TableReservation.objects.filter(
            table=table,
            reservation_date=date_obj,
            status__in=['PENDING', 'CONFIRMED'],
            start_time__lt=end_time_obj,
            end_time__gt=start_time_obj,
        ).exists()

        if is_taken:
            messages.error(
                request,
                f"Table {table.table_number} was just booked for this time slot by another customer. Please choose another table."
            )
            return redirect('reservations:book')

        reservation = TableReservation.objects.create(
            reservation_number=TableReservation.generate_reservation_number(),
            customer=request.user,
            customer_name=request.user.get_full_name() or request.user.username,
            customer_email=request.user.email,
            customer_phone=phone,
            table=table,
            reservation_date=date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            guest_count=draft['guests'],
            status='CONFIRMED',
            special_request=special_request,
        )

        # Clear session draft
        request.session.pop('reservation_draft', None)

        # Send confirmation email
        send_reservation_confirmation_email(reservation)

        messages.success(request, f"Table Reservation #{reservation.reservation_number} confirmed!")
        return redirect('reservations:detail', reservation_number=reservation.reservation_number)


@method_decorator(login_required, name='dispatch')
class ReservationDetailView(View):
    """View details of a specific reservation."""

    def get(self, request, reservation_number):
        res = get_object_or_404(TableReservation, reservation_number=reservation_number)
        if res.customer != request.user and not request.user.is_staff:
            raise PermissionDenied("You do not have permission to view this reservation.")

        context = {
            'reservation': res,
            'page_title': f'Reservation #{res.reservation_number}',
        }
        return render(request, 'reservations/detail.html', context)


@method_decorator(login_required, name='dispatch')
class MyReservationsView(View):
    """Customer account reservations list."""

    def get(self, request):
        reservations = request.user.reservations.all().order_by('-reservation_date', '-start_time')
        context = {
            'reservations': reservations,
            'today': date.today(),
            'page_title': 'My Table Reservations',
        }
        return render(request, 'reservations/reservations.html', context)


@method_decorator(login_required, name='dispatch')
class CancelReservationView(View):
    """Cancel an active upcoming table reservation."""

    def post(self, request, reservation_number):
        res = get_object_or_404(TableReservation, reservation_number=reservation_number)
        if res.customer != request.user and not request.user.is_staff:
            raise PermissionDenied("You cannot cancel another customer's reservation.")

        if res.status != 'CONFIRMED':
            messages.warning(request, f"This reservation is already {res.get_status_display().lower()}.")
            return redirect('reservations:my_reservations')

        res.status = 'CANCELLED'
        res.save(update_fields=['status'])

        send_reservation_cancellation_email(res)
        messages.info(request, f"Reservation #{res.reservation_number} has been cancelled.")
        return redirect('reservations:my_reservations')

