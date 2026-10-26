from django.urls import path

from . import views
from .api_views import SoilClassificationAPIView

app_name = "soil_classification"

urlpatterns = [
    path("", views.soil_form_view, name="form"),
    path("result/<int:pk>/", views.soil_result_view, name="result"),
    path("history/", views.soil_history_view, name="history"),
    path("api/predict/", SoilClassificationAPIView.as_view(), name="api_predict"),
]
