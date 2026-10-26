from django.conf import settings


def site_context(request):
    """Global template context available on every page."""
    return {
        "SITE_NAME": "SprigAI",
        "SITE_TAGLINE": "Smart Crop Guardian",
        "CHATBOT_PROVIDER": settings.CHATBOT_PROVIDER,
        "MAX_UPLOAD_MB": settings.MAX_UPLOAD_SIZE_MB,
        "GOOGLE_OAUTH_ENABLED": settings.GOOGLE_OAUTH_ENABLED,
        "CONTACT_EMAIL": "info@sprigai.com",
        "CONTACT_PHONE": "+880 1XXX-XXXXXX",
        "CONTACT_PHONE_TEL": "+8801XXXXXXXXX",
        "SOCIAL_LINKEDIN": "https://www.linkedin.com/",
        "SOCIAL_FACEBOOK": "https://www.facebook.com/",
        "SOCIAL_TWITTER": "https://x.com/",
        "SOCIAL_YOUTUBE": "https://www.youtube.com/",
        "nav_mode": "solid",
    }
