from django.test import TestCase
from django.urls import reverse


class PublicPageTests(TestCase):
    def test_landing_page_loads(self):
        resp = self.client.get(reverse("core:landing"))
        self.assertEqual(resp.status_code, 200)

    def test_about_page_loads(self):
        resp = self.client.get(reverse("core:about"))
        self.assertEqual(resp.status_code, 200)

    def test_features_page_loads(self):
        resp = self.client.get(reverse("core:features"))
        self.assertEqual(resp.status_code, 200)

    def test_faq_page_loads(self):
        resp = self.client.get(reverse("core:faq"))
        self.assertEqual(resp.status_code, 200)

    def test_unknown_url_returns_404(self):
        resp = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(resp.status_code, 404)
