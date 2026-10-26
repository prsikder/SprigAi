from django.urls import path

from . import views
from .api_views import CropRecommendationAPIView

app_name = "crop_recommendation"

urlpatterns = [
    path("", views.crop_form_view, name="form"),
    path("result/<int:pk>/", views.crop_result_view, name="result"),
    path("history/", views.crop_history_view, name="history"),
    path("api/predict/", CropRecommendationAPIView.as_view(), name="api_predict"),
]
