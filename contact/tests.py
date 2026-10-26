from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactTests(TestCase):
    def test_contact_form_saves_message(self):
        resp = self.client.post(reverse("contact:contact"), {
            "name": "Test User", "email": "test@example.com",
            "subject": "Hello", "message": "This is a test message.",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_page_loads(self):
        resp = self.client.get(reverse("contact:contact"))
        self.assertEqual(resp.status_code, 200)
