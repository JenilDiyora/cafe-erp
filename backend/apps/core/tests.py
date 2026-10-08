from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import CafeSetting, OpeningHour


class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cafe = CafeSetting.objects.create(
            cafe_name="Test Cafe",
            tagline="Great coffee",
            is_active=True
        )
        self.hour = OpeningHour.objects.create(
            day="Monday",
            opening_time="08:00 AM",
            closing_time="10:00 PM",
            is_closed=False,
            display_order=1
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cafe")
        self.assertContains(response, "Great coffee")

    def test_about_page_status(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Our Mission")

    def test_robots_txt(self):
        response = self.client.get(reverse('core:robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("User-agent", response.content.decode())

    def test_sitemap_xml(self):
        response = self.client.get(reverse('core:sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("<urlset", response.content.decode())

