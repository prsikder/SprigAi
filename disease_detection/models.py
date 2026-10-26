from django.conf import settings
from django.db import models


class DiseasePredictionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="disease_predictions")
    image = models.ImageField(upload_to=settings.DISEASE_UPLOAD_SUBDIR + "/")
    predicted_disease = models.CharField(max_length=100)
    confidence = models.FloatField()
    top_predictions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Disease Prediction History"
        verbose_name_plural = "Disease Prediction History"

    def __str__(self):
        return f"{self.user} - {self.predicted_disease} ({self.created_at:%Y-%m-%d})"
