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
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

