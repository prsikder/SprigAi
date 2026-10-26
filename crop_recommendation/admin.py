from django.contrib import admin
from .models import CropPredictionHistory


@admin.register(CropPredictionHistory)
class CropPredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "predicted_crop", "district", "season", "used_fallback", "created_at"]
    list_filter = ["district", "season", "used_fallback"]
    search_fields = ["user__username", "predicted_crop"]
