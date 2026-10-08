from django.test import TestCase, Client
from django.urls import reverse
from apps.gallery.models import GalleryCategory, GalleryImage


class GalleryViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = GalleryCategory.objects.create(name="Interior", slug="interior")
        self.image = GalleryImage.objects.create(
            category=self.category,
            title="Cozy Corner",
            caption="Sunlight by the window",
            is_active=True
        )

    def test_gallery_page_status(self):
        response = self.client.get(reverse('gallery:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cozy Corner")
        self.assertContains(response, "Interior")

    def test_gallery_category_filter(self):
        response = self.client.get(reverse('gallery:list') + '?category=interior')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cozy Corner")

