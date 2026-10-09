"""URL configuration for Cafe Tables & QR ordering."""
from django.urls import path
from .views import TableEntryView, ClearTableSessionView, AdminQRPrintView

app_name = 'tables'

urlpatterns = [
    path('<str:qr_token>/', TableEntryView.as_view(), name='table_entry'),
    path('session/clear/', ClearTableSessionView.as_view(), name='clear_session'),
    path('admin/qr/<int:table_id>/print/', AdminQRPrintView.as_view(), name='qr_print'),
]

