"""
AI service layer for Crop Disease Detection.
Wraps the shared ImageClassifierService with disease-specific configuration
(read from ai_models/disease_detection/metrics.json) and advisory info.
"""
import json
import logging

from django.conf import settings

from core.services.image_model_service import ImageClassifierService

logger = logging.getLogger("sprigai")

_predictor = None

GENERAL_ADVISORY = (
    "We don't have detailed guidance for this specific condition yet. "
    "As a general precaution: isolate the affected plant(s) if possible, "
    "avoid excess moisture on leaves, and consult your local agricultural "
    "extension officer or expert before applying any chemical treatment."
)

# Short, general advisory notes. Extend this as more verified information
# becomes available - keep entries concise and non-prescriptive about doses.
DISEASE_INFO = {
    "Apple_Black_Rot": "Fungal disease causing dark, sunken lesions on fruit and leaves. Remove and destroy infected plant debris; ensure good air circulation.",
    "Corn_Common_Rust": "Reddish-brown pustules appear on leaves. Favors cool, humid weather. Consider resistant varieties for future planting.",
    "Grape_Black_rot": "Causes dark leaf spots and shriveled fruit. Prune infected canes and remove mummified fruit to reduce spread.",
    "Potato_Late_Blight": "Serious fungal-like disease causing dark, water-soaked lesions. Spreads quickly in wet weather - act promptly and consult an expert.",
    "Rice_Neck_Blast": "Affects the rice panicle neck, causing yield loss. Avoid excess nitrogen fertilizer and ensure proper field drainage.",
    "Strawberry_Leaf_Scroch": "Causes purplish spots and leaf scorching. Remove infected leaves and avoid overhead watering.",
    "Tomato_Bacterial_Spot": "Causes small, dark, greasy-looking spots on leaves and fruit. Avoid working with wet plants; rotate crops.",
    "Wheat_Brown_Rust": "Orange-brown pustules on leaves, reducing yield. Monitor closely during humid conditions; resistant varieties help.",
}

HEALTHY_KEYWORDS = ("healthy",)


def is_healthy_label(label: str) -> bool:
    return any(k in label.lower() for k in HEALTHY_KEYWORDS)


def get_advisory(label: str) -> str:
    if is_healthy_label(label):
        return "Good news - this plant appears healthy. Keep monitoring regularly and maintain good field hygiene."
    return DISEASE_INFO.get(label, GENERAL_ADVISORY)


def _get_predictor():
    global _predictor
    if _predictor is not None:
        return _predictor

    mean, std, image_size = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225], 224
    metrics_path = settings.DISEASE_MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
            mean = metrics.get("mean", mean)
            std = metrics.get("std", std)
            image_size = metrics.get("image_size", image_size)
        except Exception:
            logger.exception("Could not read disease_detection metrics.json, using defaults")

    _predictor = ImageClassifierService(
        name="Crop Disease Detection",
        weights_path=settings.DISEASE_MODEL_DIR / "crop_disease_model.pth",
        class_names_path=settings.DISEASE_MODEL_DIR / "class_names.json",
        mean=mean, std=std, image_size=image_size,
    )
    return _predictor


def predict_disease(django_file):
    result = _get_predictor().predict(django_file, top_k=3)
    if result.get("success"):
        result["advisory"] = get_advisory(result["predicted_class"])
        result["is_healthy"] = is_healthy_label(result["predicted_class"])
    return result
