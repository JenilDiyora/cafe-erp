from django.test import TestCase, Client
from django.urls import reverse
from apps.reviews.models import Review


class ReviewsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.review = Review.objects.create(
            customer_name="Pooja Patel",
            rating=5,
            review_text="Best cold brew in town!",
            is_featured=True,
            is_active=True
        )

    def test_reviews_page_status(self):
        response = self.client.get(reverse('reviews:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pooja Patel")
        self.assertContains(response, "Best cold brew in town!")
        self.assertContains(response, "Featured Highlights")

