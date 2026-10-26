from django.conf import settings
from django.db import models


class SoilPredictionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="soil_predictions")
    image = models.ImageField(upload_to=settings.SOIL_UPLOAD_SUBDIR + "/")
    predicted_soil = models.CharField(max_length=100)
    confidence = models.FloatField()
    suggested_crops = models.JSONField(default=list, blank=True)
    top_predictions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Soil Prediction History"
        verbose_name_plural = "Soil Prediction History"

    def __str__(self):
        return f"{self.user} - {self.predicted_soil} ({self.created_at:%Y-%m-%d})"
