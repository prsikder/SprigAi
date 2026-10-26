from django.conf import settings
from django.db import models


class FertilizerPredictionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fertilizer_predictions")

    soil_type = models.CharField(max_length=20)
    soil_ph = models.FloatField()
    nitrogen_level = models.FloatField(null=True, blank=True)
    phosphorus_level = models.FloatField(null=True, blank=True)
    potassium_level = models.FloatField(null=True, blank=True)
    temperature = models.FloatField()
    humidity = models.FloatField()
    crop_type = models.CharField(max_length=30)
    crop_growth_stage = models.CharField(max_length=20)
    season = models.CharField(max_length=20)
    irrigation_type = models.CharField(max_length=20)
    previous_crop = models.CharField(max_length=30)

    recommended_fertilizer = models.CharField(max_length=150)
    npk_imputed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Fertilizer Prediction History"
        verbose_name_plural = "Fertilizer Prediction History"

    def __str__(self):
        return f"{self.user} - {self.recommended_fertilizer} ({self.created_at:%Y-%m-%d})"
