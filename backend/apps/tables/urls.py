"""URL configuration for Cafe Tables & QR ordering."""
from django.urls import path
from .views import TableEntryView, ClearTableSessionView, AdminQRPrintView, AdminQRPrintAllView

app_name = 'tables'

urlpatterns = [
    path('session/clear/', ClearTableSessionView.as_view(), name='clear_session'),
    path('admin/qr/print-all/', AdminQRPrintAllView.as_view(), name='qr_print_all'),
    path('admin/qr/<int:table_id>/print/', AdminQRPrintView.as_view(), name='qr_print'),
    path('<str:qr_token>/', TableEntryView.as_view(), name='table_entry'),
]

