from django.contrib import admin

from .models import PredictionLog, SiteActivity


@admin.register(SiteActivity)
class SiteActivityAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "ip_address", "path", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "description", "path")
    readonly_fields = ("created_at",)


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ("module", "status", "user", "model_name", "duration_ms", "created_at")
    list_filter = ("module", "status", "created_at")
    search_fields = ("user__username", "model_name", "message")
    readonly_fields = ("created_at",)
