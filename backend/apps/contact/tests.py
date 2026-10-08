from django.test import TestCase, Client
from django.urls import reverse
from apps.contact.models import ContactInquiry


class ContactViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_page_get(self):
        response = self.client.get(reverse('contact:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Send Us a Message")

    def test_contact_submission_valid(self):
        data = {
            'name': 'Rahul Verma',
            'email': 'rahul@example.com',
            'phone': '+917405401350',
            'subject': 'Table Booking Query',
            'message': 'Hi, I would like to inquire about hosting a weekend book club meeting.'
        }
        response = self.client.post(reverse('contact:index'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactInquiry.objects.filter(email='rahul@example.com').exists())
        self.assertContains(response, "Thank you! Your message has been received.")

    def test_contact_submission_invalid(self):
        data = {
            'name': '',
            'email': 'not-an-email',
            'message': ''
        }
        response = self.client.post(reverse('contact:index'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactInquiry.objects.filter(email='not-an-email').exists())

