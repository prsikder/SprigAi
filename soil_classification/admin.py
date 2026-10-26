from django.contrib import admin
from .models import SoilPredictionHistory


@admin.register(SoilPredictionHistory)
class SoilPredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "predicted_soil", "confidence", "created_at"]
    list_filter = ["predicted_soil"]
    search_fields = ["user__username", "predicted_soil"]
