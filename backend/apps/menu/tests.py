from django.test import TestCase, Client
from django.urls import reverse
from apps.menu.models import Category, Product


class MenuViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Hot Coffee", slug="hot-coffee")
        self.product1 = Product.objects.create(
            category=self.category,
            name="Double Espresso",
            price=120.00,
            description="Strong dark roast",
            is_available=True,
            vegetarian=True
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name="Caramel Frappe",
            price=220.00,
            description="Sweet iced coffee",
            is_available=True,
            is_bestseller=True
        )

    def test_menu_page_status(self):
        response = self.client.get(reverse('menu:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Double Espresso")
        self.assertContains(response, "Hot Coffee")

    def test_menu_search_filter(self):
        response = self.client.get(reverse('menu:list') + '?q=Caramel')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Caramel Frappe")
        self.assertNotContains(response, "Double Espresso")

    def test_menu_category_filter(self):
        response = self.client.get(reverse('menu:list') + '?category=hot-coffee')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Double Espresso")

