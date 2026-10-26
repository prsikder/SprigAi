"""Project URL routing for SprigAI."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("crop-recommendation/", include("crop_recommendation.urls")),
    path("fertilizer-recommendation/", include("fertilizer_recommendation.urls")),
    path("disease-detection/", include("disease_detection.urls")),
    path("soil-classification/", include("soil_classification.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("contact/", include("contact.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
