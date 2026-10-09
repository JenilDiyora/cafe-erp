"""URL patterns for Customer Orders module."""
from django.urls import path
from .views import CheckoutView, OrderConfirmationView, OrderHistoryView, OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('<str:order_number>/confirmation/', OrderConfirmationView.as_view(), name='confirmation'),
    path('history/', OrderHistoryView.as_view(), name='history'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='detail'),
]

