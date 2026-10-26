from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class DiseaseDetectionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="farmer", password="StrongPass123!")
        self.client.login(username="farmer", password="StrongPass123!")

    def test_form_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("disease_detection:form"))
        self.assertEqual(resp.status_code, 302)

    def test_form_page_loads(self):
        resp = self.client.get(reverse("disease_detection:form"))
        self.assertEqual(resp.status_code, 200)

    def test_invalid_file_type_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        bad_file = SimpleUploadedFile("test.txt", b"not an image", content_type="text/plain")
        resp = self.client.post(reverse("disease_detection:form"), {"image": bad_file})
        self.assertEqual(resp.status_code, 200)  # re-renders form with error, no crash
