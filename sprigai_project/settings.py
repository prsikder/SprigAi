"""
Django settings for SprigAI - Smart Crop Guardian.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
IS_VERCEL = os.getenv("VERCEL") == "1"

# --------------------------------------------------------------------
# Core / Security
# --------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key-change-me")
if IS_VERCEL and SECRET_KEY in {"", "dev-only-insecure-key-change-me", "change-this-to-a-long-random-secret-key"}:
    raise ImproperlyConfigured("Set a unique SECRET_KEY in Vercel environment variables.")
DEBUG = os.getenv("DEBUG", "False" if IS_VERCEL else "True").lower() in {"true", "1", "yes"}
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [value.strip() for value in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if value.strip()]
if IS_VERCEL:
    for name in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
        host = os.getenv(name)
        if host:
            ALLOWED_HOSTS.append(host)
            CSRF_TRUSTED_ORIGINS.append(f"https://{host}")
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "rest_framework",
    "widget_tweaks",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "core",
    "accounts",
    "dashboard",
    "crop_recommendation",
    "fertilizer_recommendation",
    "disease_detection",
    "soil_classification",
    "chatbot",
    "contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.FriendlyErrorMiddleware",
]

ROOT_URLCONF = "sprigai_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "sprigai_project.wsgi.application"

# --------------------------------------------------------------------
# Database (MySQL via XAMPP / phpMyAdmin)
# --------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.getenv("DB_NAME", "sprigai_db"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
DATABASES["default"]["CONN_MAX_AGE"] = 0
if os.getenv("DB_SSL_CA"):
    DATABASES["default"]["OPTIONS"]["ssl"] = {"ca": os.environ["DB_SSL_CA"], "check_hostname": True}
elif os.getenv("DB_SSL", "False").lower() in {"true", "1", "yes"}:
    DATABASES["default"]["OPTIONS"]["ssl"] = {"check_hostname": True}

# --------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "core:landing"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# django-allauth (Google OAuth)
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_OAUTH_ENABLED = bool(GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET)

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
SOCIALACCOUNT_ADAPTER = "accounts.adapters.SprigSocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# --------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------
# Static & Media
# --------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DISEASE_UPLOAD_SUBDIR = "disease_uploads"
SOIL_UPLOAD_SUBDIR = "soil_uploads"

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "8"))
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------
# AI / ML model configuration
# --------------------------------------------------------------------
AI_MODELS_DIR = BASE_DIR / os.getenv("AI_MODELS_DIR", "ai_models")

CROP_MODEL_DIR = AI_MODELS_DIR / "crop_recommendation"
FERTILIZER_MODEL_DIR = AI_MODELS_DIR / "fertilizer_recommendation"
DISEASE_MODEL_DIR = AI_MODELS_DIR / "disease_detection"
SOIL_MODEL_DIR = AI_MODELS_DIR / "soil_classification"

# --------------------------------------------------------------------
# Chatbot (Gemini or OpenAI) - keys read from environment, never hardcoded
# --------------------------------------------------------------------
CHATBOT_PROVIDER = os.getenv("CHATBOT_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --------------------------------------------------------------------
# REST Framework
# --------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# --------------------------------------------------------------------
# Logging - never print() in production views; use logger.exception
# --------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "sprigai.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "sprigai": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
}
if IS_VERCEL:
    LOGGING["handlers"].pop("file")
    LOGGING["root"]["handlers"] = ["console"]
    for config in LOGGING["loggers"].values():
        config["handlers"] = ["console"]
else:
    os.makedirs(BASE_DIR / "logs", exist_ok=True)

MESSAGE_TAGS = {}
