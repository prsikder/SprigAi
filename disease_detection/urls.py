from django.urls import path

from . import views
from .api_views import DiseaseDetectionAPIView

app_name = "disease_detection"

urlpatterns = [
    path("", views.disease_form_view, name="form"),
    path("result/<int:pk>/", views.disease_result_view, name="result"),
    path("history/", views.disease_history_view, name="history"),
    path("api/predict/", DiseaseDetectionAPIView.as_view(), name="api_predict"),
]
