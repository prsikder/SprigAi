from django.urls import path

from . import views
from .api_views import FertilizerRecommendationAPIView

app_name = "fertilizer_recommendation"

urlpatterns = [
    path("", views.fertilizer_form_view, name="form"),
    path("result/<int:pk>/", views.fertilizer_result_view, name="result"),
    path("history/", views.fertilizer_history_view, name="history"),
    path("api/predict/", FertilizerRecommendationAPIView.as_view(), name="api_predict"),
]
