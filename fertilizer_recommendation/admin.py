from django.contrib import admin
from .models import FertilizerPredictionHistory


@admin.register(FertilizerPredictionHistory)
class FertilizerPredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "recommended_fertilizer", "crop_type", "soil_type", "npk_imputed", "created_at"]
    list_filter = ["soil_type", "crop_type", "season", "npk_imputed"]
    search_fields = ["user__username", "recommended_fertilizer"]
