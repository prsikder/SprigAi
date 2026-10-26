from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class FertilizerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="farmer", password="StrongPass123!")
        self.client.login(username="farmer", password="StrongPass123!")

    def test_form_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("fertilizer_recommendation:form"))
        self.assertEqual(resp.status_code, 302)

    def test_form_page_loads(self):
        resp = self.client.get(reverse("fertilizer_recommendation:form"))
        self.assertEqual(resp.status_code, 200)

    def test_npk_optional_in_form(self):
        from .forms import FertilizerRecommendationForm
        form = FertilizerRecommendationForm(data={
            "soil_type": "Loamy", "soil_ph": 6.5, "temperature": 28, "humidity": 60,
            "crop_type": "Rice", "crop_growth_stage": "Sowing", "season": "Kharif",
            "irrigation_type": "Canal", "previous_crop": "Wheat",
        })
        self.assertTrue(form.is_valid(), form.errors)
