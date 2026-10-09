"""WSGI config for cafe website."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

# Ensure database tables and initial cafe data exist on production container boot
try:
    from django.core.management import call_command
    from django.db import connection

    tables = connection.introspection.table_names()
    needs_seeding = False

    if 'gallery_galleryimage' not in tables:
        call_command('migrate', interactive=False)
        needs_seeding = True
    else:
        from apps.gallery.models import GalleryImage
        if not GalleryImage.objects.exists():
            needs_seeding = True

    if needs_seeding:
        call_command('seed_cafe_data')
        call_command('seed_phase2_data')
        call_command('populate_photos')
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Startup auto-migration/seed skipped: %s", e)

