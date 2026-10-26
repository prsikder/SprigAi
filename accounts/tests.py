from django.test import TestCase
from django.urls import reverse

from .models import User


class SignupLoginTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        resp = self.client.post(reverse("accounts:signup"), {
            "username": "farmer1", "first_name": "Farmer", "last_name": "One",
            "email": "farmer1@example.com", "phone": "", "district": "Sylhet",
            "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertEqual(User.objects.filter(username="farmer1").count(), 1)
        self.assertEqual(resp.status_code, 302)

    def test_login_with_email(self):
        User.objects.create_user(username="farmer2", email="farmer2@example.com", password="StrongPass123!")
        resp = self.client.post(reverse("accounts:login"), {"username": "farmer2@example.com", "password": "StrongPass123!"})
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse("dashboard:home"))
        self.assertEqual(resp.status_code, 302)
