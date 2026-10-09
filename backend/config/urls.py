"""Main URL configuration for Cafe website."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom error handlers
handler404 = 'apps.core.views.custom_404_view'
handler500 = 'apps.core.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('menu/', include('apps.menu.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('contact/', include('apps.contact.urls')),
    path('account/', include('apps.accounts.urls', namespace='accounts')),
    path('table/', include('apps.tables.urls', namespace='tables')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('reservations/', include('apps.reservations.urls', namespace='reservations')),
]

from django.urls import re_path
from django.views.static import serve

# Serve media files in all environments (essential for Render free tier)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

