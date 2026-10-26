"""
AI service layer for Crop Recommendation.

Loads the trained RandomForest classifier/regressor and the four
LabelEncoders shipped in ai_models/crop_recommendation/, and exposes a
single predict_crop(...) function that ALWAYS returns a structured dict
and never raises an exception the view has not already anticipated.

Model contract (discovered from the shipped .pkl files):
  Features (both classifier & regressor), in this exact order:
      ['Area', 'District', 'Season', 'Current_Temp', 'Current_Humidity', 'Growing_Time']
  rf_classifier.pkl  -> MultiOutputClassifier-like output of shape (2,):
      output[0] = encoded crop label   (72 classes, see crop_encoder.pkl)
      output[1] = encoded harvest label (34 classes, see harvest_encoder.pkl)
  rf_regressor.pkl -> 3 numeric outputs, in this order:
      [Production, Suitable_Avg_Temperature, Suitable_Avg_Humidity]
  (This ordering matches the "Outputs" section of the project spec and the
  feature/target shapes found in the shipped model files. If your original
  training notebook used a different regression target order, update
  REGRESSION_OUTPUT_ORDER below - nothing else needs to change.)
"""
import difflib
import logging
import threading

import joblib
from django.conf import settings

logger = logging.getLogger("sprigai")

REGRESSION_OUTPUT_ORDER = ["production", "suitable_temperature", "suitable_humidity"]

_lock = threading.Lock()
_cache = {}

DISPLAY_NAME_FIXES = {
    "Lady\u95f3\u30e6\u7378 Finger": "Lady's Finger (Okra)",
}


class ModelNotAvailableError(Exception):
    pass


def _load_pickle(filename):
    path = settings.CROP_MODEL_DIR / filename
    if not path.exists():
        raise ModelNotAvailableError(f"Required model file is missing: {filename}. "
                                      f"Place it in {settings.CROP_MODEL_DIR}")
    return joblib.load(path)


def _get_models():
    """Thread-safe lazy singleton loader so models are read from disk once."""
    if _cache:
        return _cache
    with _lock:
        if not _cache:
            try:
                _cache["crop_encoder"] = _load_pickle("crop_encoder.pkl")
                _cache["district_encoder"] = _load_pickle("district_encoder.pkl")
                _cache["growth_encoder"] = _load_pickle("growth_encoder.pkl")
                _cache["harvest_encoder"] = _load_pickle("harvest_encoder.pkl")
                _cache["season_encoder"] = _load_pickle("season_encoder.pkl")
                _cache["rf_classifier"] = _load_pickle("rf_classifier.pkl")
                _cache["rf_regressor"] = _load_pickle("rf_regressor.pkl")
            except ModelNotAvailableError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to load crop recommendation models")
                raise ModelNotAvailableError(str(exc)) from exc
    return _cache


def _safe_encode(encoder, value, field_label):
    """
    Encode a categorical value. If it is unseen, fall back to the closest
    known category (case-insensitive fuzzy match) instead of crashing.
    Returns (encoded_int, used_fallback: bool, resolved_value: str).
    """
    classes = list(encoder.classes_)
    if value in classes:
        return int(encoder.transform([value])[0]), False, value

    # try case-insensitive exact match
    lower_map = {c.lower(): c for c in classes}
    if value.lower() in lower_map:
        matched = lower_map[value.lower()]
        return int(encoder.transform([matched])[0]), True, matched

    # try whitespace-normalized match
    norm_map = {" ".join(c.split()).lower(): c for c in classes}
    norm_value = " ".join(value.split()).lower()
    if norm_value in norm_map:
        matched = norm_map[norm_value]
        return int(encoder.transform([matched])[0]), True, matched

    # fuzzy nearest match as a last resort
    close = difflib.get_close_matches(value, classes, n=1, cutoff=0.5)
    if close:
        matched = close[0]
        logger.info("crop_service: unseen %s '%s' fell back to closest match '%s'", field_label, value, matched)
        return int(encoder.transform([matched])[0]), True, matched

    # absolute fallback: first known class, clearly flagged
    matched = classes[0]
    logger.warning("crop_service: unseen %s '%s' had no close match, defaulted to '%s'", field_label, value, matched)
    return int(encoder.transform([matched])[0]), True, matched


def predict_crop(area, district, season, current_temp, current_humidity, growing_time):
    """
    Returns a dict:
      {
        "success": bool,
        "error": str | None,
        "used_fallback": bool,
        "crop": str, "harvest": str,
        "production": float | None,
        "suitable_temperature": float | None,
        "suitable_humidity": float | None,
      }
    Never raises - all errors are captured and returned as structured data
    so the view can render a friendly message instead of a crash.
    """
    try:
        models = _get_models()
    except ModelNotAvailableError as exc:
        return {"success": False, "error": f"Crop recommendation model is currently unavailable: {exc}"}

    try:
        used_fallback = False

        dist_code, fb1, _ = _safe_encode(models["district_encoder"], district, "district")
        season_code, fb2, _ = _safe_encode(models["season_encoder"], season, "season")
        growth_code, fb3, _ = _safe_encode(models["growth_encoder"], growing_time, "growing_time")
        used_fallback = fb1 or fb2 or fb3

        import numpy as np
        X = np.array([[float(area), dist_code, season_code, float(current_temp), float(current_humidity), growth_code]])

        clf = models["rf_classifier"]
        pred = clf.predict(X)[0]
        crop_code, harvest_code = int(pred[0]), int(pred[1])

        crop_classes = list(models["crop_encoder"].classes_)
        harvest_classes = list(models["harvest_encoder"].classes_)
        crop_name = crop_classes[crop_code] if 0 <= crop_code < len(crop_classes) else "Unknown"
        harvest_name = harvest_classes[harvest_code] if 0 <= harvest_code < len(harvest_classes) else "Unknown"
        crop_name = DISPLAY_NAME_FIXES.get(crop_name, crop_name)

        reg = models["rf_regressor"]
        reg_pred = reg.predict(X)[0]
        reg_values = {}
        for i, key in enumerate(REGRESSION_OUTPUT_ORDER):
            reg_values[key] = round(float(reg_pred[i]), 2) if i < len(reg_pred) else None

        return {
            "success": True,
            "error": None,
            "used_fallback": used_fallback,
            "crop": crop_name,
            "harvest": harvest_name,
            "production": reg_values.get("production"),
            "suitable_temperature": reg_values.get("suitable_temperature"),
            "suitable_humidity": reg_values.get("suitable_humidity"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Crop prediction failed")
        return {"success": False, "error": "We couldn't generate a crop recommendation from these inputs. Please check your values and try again."}
