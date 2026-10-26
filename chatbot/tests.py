from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .services.chatbot_service import get_bot_reply


class ChatbotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="farmer", password="StrongPass123!")
        self.client.login(username="farmer", password="StrongPass123!")

    def test_chat_page_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("chatbot:chat"))
        self.assertEqual(resp.status_code, 302)

    def test_chat_page_loads(self):
        resp = self.client.get(reverse("chatbot:chat"))
        self.assertEqual(resp.status_code, 200)

    def test_missing_api_key_does_not_crash(self):
        # With no GEMINI_API_KEY/OPENAI_API_KEY configured, this should return
        # a graceful fallback message instead of raising.
        result = get_bot_reply("How do I grow rice?")
        self.assertIn("reply", result)
