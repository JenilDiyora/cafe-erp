from django.shortcuts import render, get_object_or_404
from django.views import View

from apps.core.models import CafeSetting
from .models import GalleryCategory, GalleryImage


class GalleryView(View):
    """Gallery page with category filters and responsive lightbox viewing."""

    def get(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        categories = GalleryCategory.objects.filter(is_active=True).order_by('display_order', 'name')

        images = GalleryImage.objects.filter(is_active=True).select_related('category')

        selected_category_slug = request.GET.get('category', '').strip()
        selected_category = None
        if selected_category_slug and selected_category_slug != 'all':
            selected_category = get_object_or_404(GalleryCategory, slug=selected_category_slug, is_active=True)
            images = images.filter(category=selected_category)

        images = images.order_by('display_order', '-created_at')

        context = {
            'page_title': 'Photo Gallery',
            'cafe_settings': cafe_settings,
            'categories': categories,
            'images': images,
            'selected_category': selected_category,
            'selected_category_slug': selected_category_slug or 'all',
            'request': request,
        }
        return render(request, 'gallery/gallery.html', context)

