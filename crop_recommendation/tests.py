from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .services.crop_service import _safe_encode
import joblib
from django.conf import settings


class CropServiceTests(TestCase):
    def test_unseen_district_falls_back_safely(self):
        encoder = joblib.load(settings.CROP_MODEL_DIR / "district_encoder.pkl")
        code, used_fallback, resolved = _safe_encode(encoder, "NotARealDistrict", "district")
        self.assertTrue(used_fallback)
        self.assertIn(resolved, list(encoder.classes_))


class CropViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="farmer", password="StrongPass123!")
        self.client.login(username="farmer", password="StrongPass123!")

    def test_form_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("crop_recommendation:form"))
        self.assertEqual(resp.status_code, 302)

    def test_form_page_loads(self):
        resp = self.client.get(reverse("crop_recommendation:form"))
        self.assertEqual(resp.status_code, 200)
