from django.conf import settings
from django.db import models


class SiteActivity(models.Model):
    class Action(models.TextChoices):
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PROFILE_UPDATE = "profile_update", "Profile Update"
        CONTACT_SUBMIT = "contact_submit", "Contact Submit"
        PREDICTION = "prediction", "Prediction"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="site_activities",
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=40, choices=Action.choices, default=Action.OTHER)
    description = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    path = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "site activities"

    def __str__(self):
        return f"{self.get_action_display()} at {self.created_at:%Y-%m-%d %H:%M}"


class PredictionLog(models.Model):
    class Module(models.TextChoices):
        CROP = "crop_recommendation", "Crop Recommendation"
        FERTILIZER = "fertilizer_recommendation", "Fertilizer Recommendation"
        DISEASE = "disease_detection", "Disease Detection"
        SOIL = "soil_classification", "Soil Classification"
        CHATBOT = "chatbot", "Chatbot"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        MODEL_MISSING = "model_missing", "Model Missing"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="prediction_logs",
        blank=True,
        null=True,
    )
    module = models.CharField(max_length=40, choices=Module.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    model_name = models.CharField(max_length=160, blank=True)
    message = models.CharField(max_length=255, blank=True)
    duration_ms = models.PositiveIntegerField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_module_display()} - {self.get_status_display()}"
