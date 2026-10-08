from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from apps.core.models import CafeSetting, OpeningHour
from apps.menu.models import Product, Category
from apps.gallery.models import GalleryImage
from apps.reviews.models import Review


class HomeView(View):
    """Homepage view rendering hero, featured items, about preview, highlights, reviews, and gallery."""
    def get(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        opening_hours = OpeningHour.objects.filter(is_active=True).order_by('display_order', 'id')
        featured_products = Product.objects.filter(
            is_featured=True,
            is_available=True
        ).select_related('category')[:6]

        bestsellers = Product.objects.filter(
            is_bestseller=True,
            is_available=True
        ).select_related('category')[:4]

        # If not enough featured, take general available items
        if not featured_products.exists():
            featured_products = Product.objects.filter(is_available=True).select_related('category')[:6]

        reviews = Review.objects.filter(is_active=True).order_by('-rating', 'display_order')[:3]
        gallery_images = GalleryImage.objects.filter(is_active=True).select_related('category')[:6]
        categories = Category.objects.filter(is_active=True).order_by('display_order')[:6]

        context = {
            'page_title': 'Home',
            'cafe_settings': cafe_settings,
            'opening_hours': opening_hours,
            'featured_products': featured_products,
            'bestsellers': bestsellers,
            'reviews': reviews,
            'gallery_images': gallery_images,
            'categories': categories,
            'request': request,
        }
        return render(request, 'home/index.html', context)


class AboutView(View):
    """About us page detailing cafe story, philosophy, and team."""
    def get(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        opening_hours = OpeningHour.objects.filter(is_active=True).order_by('display_order', 'id')

        context = {
            'page_title': 'About Us',
            'cafe_settings': cafe_settings,
            'opening_hours': opening_hours,
            'request': request,
        }
        return render(request, 'about/about.html', context)


def custom_404_view(request, exception=None):
    """Custom 404 error handler."""
    context = {'page_title': 'Page Not Found', 'request': request}
    return render(request, 'errors/404.html', context, status=404)


def custom_500_view(request):
    """Custom 500 error handler."""
    context = {'page_title': 'Server Error', 'request': request}
    return render(request, 'errors/500.html', context, status=500)


def robots_txt_view(request):
    """Robots.txt for search engines."""
    content = "User-agent: *\nDisallow: /admin/\nAllow: /\n\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml_view(request):
    """Sitemap.xml for SEO indexing."""
    scheme = request.scheme
    host = request.get_host()
    urls = [
        '',
        '/menu/',
        '/about/',
        '/gallery/',
        '/reviews/',
        '/contact/',
    ]
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in urls:
        xml_lines.append(f'  <url><loc>{scheme}://{host}{path}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    xml_lines.append('</urlset>')
    return HttpResponse('\n'.join(xml_lines), content_type="application/xml")
