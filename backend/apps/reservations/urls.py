"""URL patterns for Table Reservations module."""
from django.urls import path
from .views import (
    BookTableView,
    ConfirmReservationView,
    ReservationDetailView,
    MyReservationsView,
    CancelReservationView
)

app_name = 'reservations'

urlpatterns = [
    path('book/', BookTableView.as_view(), name='book'),
    path('confirm/', ConfirmReservationView.as_view(), name='confirm'),
    path('my-reservations/', MyReservationsView.as_view(), name='my_reservations'),
    path('<str:reservation_number>/', ReservationDetailView.as_view(), name='detail'),
    path('<str:reservation_number>/cancel/', CancelReservationView.as_view(), name='cancel'),
]

