"""
AI service layer for Soil Classification.
Wraps the shared ImageClassifierService with soil-specific configuration
(read from ai_models/soil_classification/metrics.json) and crop suggestions.
"""
import json
import logging

from django.conf import settings

from core.services.image_model_service import ImageClassifierService

logger = logging.getLogger("sprigai")

_predictor = None

# Soil type -> suitable crops, from the project specification.
SOIL_CROP_SUGGESTIONS = {
    "Alluvial_Soil": ["Rice", "Jute", "Wheat", "Potato", "Mustard", "Lentil", "Chickpea", "Maize",
                       "Sugarcane", "Onion", "Garlic", "Tomato", "Eggplant (Brinjal)", "Cabbage", "Cauliflower"],
    "Arid_Soil": ["Wheat", "Mustard", "Groundnut", "Sesame", "Chickpea", "Cumin", "Date Palm"],
    "Black_Soil": ["Cotton", "Soybean", "Wheat", "Sugarcane", "Sunflower", "Tobacco", "Sorghum", "Maize",
                    "Groundnut", "Pulses"],
    "Laterite_Soil": ["Tea", "Coffee", "Cashew", "Coconut", "Rubber", "Pineapple", "Sweet Potato",
                       "Groundnut", "Mango", "Jackfruit"],
    "Red_Soil": ["Maize", "Potato", "Groundnut", "Mango", "Guava"],
    "Yellow_Soil": ["Tea", "Pineapple", "Ginger", "Turmeric", "Banana", "Orange", "Lemon", "Maize",
                     "Potato", "Black Pepper"],
}


def get_crop_suggestions(soil_label: str):
    return SOIL_CROP_SUGGESTIONS.get(soil_label, [])


def _get_predictor():
    global _predictor
    if _predictor is not None:
        return _predictor

    mean, std, image_size = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225], 224
    metrics_path = settings.SOIL_MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
            mean = metrics.get("mean", mean)
            std = metrics.get("std", std)
            image_size = metrics.get("image_size", metrics.get("img_size", image_size))
        except Exception:
            logger.exception("Could not read soil_classification metrics.json, using defaults")

    _predictor = ImageClassifierService(
        name="Soil Classification",
        weights_path=settings.SOIL_MODEL_DIR / "soil_classifier.pth",
        class_names_path=settings.SOIL_MODEL_DIR / "class_names.json",
        mean=mean, std=std, image_size=image_size,
    )
    return _predictor


def predict_soil(django_file):
    result = _get_predictor().predict(django_file, top_k=3)
    if result.get("success"):
        result["suggested_crops"] = get_crop_suggestions(result["predicted_class"])
    return result
