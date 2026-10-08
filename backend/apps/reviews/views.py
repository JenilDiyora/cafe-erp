from django.shortcuts import render
from django.views import View
from django.db.models import Avg

from apps.core.models import CafeSetting
from .models import Review


class ReviewsView(View):
    """Customer testimonials and reviews page."""

    def get(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        reviews = Review.objects.filter(is_active=True).order_by('display_order', '-created_at')

        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 5.0
        avg_rating_rounded = round(avg_rating, 1)

        featured_reviews = reviews.filter(is_featured=True)[:3]

        context = {
            'page_title': 'Customer Reviews',
            'cafe_settings': cafe_settings,
            'reviews': reviews,
            'featured_reviews': featured_reviews,
            'total_reviews': reviews.count(),
            'avg_rating': avg_rating_rounded,
            'request': request,
        }
        return render(request, 'reviews/reviews.html', context)

