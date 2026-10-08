from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Q

from apps.core.models import CafeSetting
from .models import Category, Product


class MenuView(View):
    """Cafe menu view supporting category tabs, keyword search, and dietary filters."""

    def get(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')

        products = Product.objects.all().select_related('category')

        # Filter by category
        selected_category_slug = request.GET.get('category', '').strip()
        selected_category = None
        if selected_category_slug and selected_category_slug != 'all':
            selected_category = get_object_or_404(Category, slug=selected_category_slug, is_active=True)
            products = products.filter(category=selected_category)

        # Filter by search keyword
        query = request.GET.get('q', '').strip()
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(category__name__icontains=query)
            )

        # Filter by vegetarian
        veg_filter = request.GET.get('veg', '').strip()
        if veg_filter == '1':
            products = products.filter(vegetarian=True)

        # Filter by spicy
        spicy_filter = request.GET.get('spicy', '').strip()
        if spicy_filter == '1':
            products = products.filter(spicy=True)

        # Filter by bestseller
        bestseller_filter = request.GET.get('bestseller', '').strip()
        if bestseller_filter == '1':
            products = products.filter(is_bestseller=True)

        products = products.order_by('display_order', 'name')

        # Group products by category for easy structured browsing if viewing all
        categorized_products = []
        if not selected_category and not query and not veg_filter and not spicy_filter and not bestseller_filter:
            for cat in categories:
                cat_products = products.filter(category=cat)
                if cat_products.exists():
                    categorized_products.append({
                        'category': cat,
                        'products': cat_products,
                    })

        context = {
            'page_title': 'Our Menu',
            'cafe_settings': cafe_settings,
            'categories': categories,
            'products': products,
            'categorized_products': categorized_products,
            'selected_category': selected_category,
            'selected_category_slug': selected_category_slug or 'all',
            'query': query,
            'veg_filter': veg_filter,
            'spicy_filter': spicy_filter,
            'bestseller_filter': bestseller_filter,
            'request': request,
        }
        return render(request, 'menu/menu.html', context)

