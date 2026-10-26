from django.contrib import admin
from .models import DiseasePredictionHistory


@admin.register(DiseasePredictionHistory)
class DiseasePredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "predicted_disease", "confidence", "created_at"]
    list_filter = ["predicted_disease"]
    search_fields = ["user__username", "predicted_disease"]
