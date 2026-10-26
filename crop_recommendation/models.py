from django.conf import settings
from django.db import models


class CropPredictionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crop_predictions")

    # Inputs
    area = models.FloatField()
    district = models.CharField(max_length=50)
    season = models.CharField(max_length=20)
    current_temp = models.FloatField()
    current_humidity = models.FloatField()
    growing_time = models.CharField(max_length=50)

    # Outputs
    predicted_crop = models.CharField(max_length=100)
    predicted_harvest = models.CharField(max_length=100, blank=True)
    production = models.FloatField(null=True, blank=True)
    suitable_temperature = models.FloatField(null=True, blank=True)
    suitable_humidity = models.FloatField(null=True, blank=True)

    used_fallback = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Crop Prediction History"
        verbose_name_plural = "Crop Prediction History"

    def __str__(self):
        return f"{self.user} - {self.predicted_crop} ({self.created_at:%Y-%m-%d})"
