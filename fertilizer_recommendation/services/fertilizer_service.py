"""
AI service layer for Fertilizer Recommendation.

Loads the trained CatBoost model plus its input-column and categorical-
feature metadata from ai_models/fertilizer_recommendation/, and exposes
predict_fertilizer(...) which always returns a structured dict and never
raises an exception the view hasn't already anticipated.

CatBoost handles categorical columns natively (no separate LabelEncoder
files are shipped), so unseen categories do not crash prediction - CatBoost
simply treats them as an "unknown" category internally. NPK values are
optional; if omitted we impute a safe default defined in constants.py.
"""
import logging
import threading

import joblib
from django.conf import settings

from ..constants import DEFAULT_NITROGEN, DEFAULT_PHOSPHORUS, DEFAULT_POTASSIUM

logger = logging.getLogger("sprigai")

_lock = threading.Lock()
_cache = {}

# Some datasets spell the third season "Zahid" instead of "Zaid".
SEASON_ALIASES = {"zaid": "Zaid", "zahid": "Zaid"}


class ModelNotAvailableError(Exception):
    pass


def _load_pickle(filename):
    path = settings.FERTILIZER_MODEL_DIR / filename
    if not path.exists():
        raise ModelNotAvailableError(f"Required model file is missing: {filename}. "
                                      f"Place it in {settings.FERTILIZER_MODEL_DIR}")
    return joblib.load(path)


def _get_models():
    if _cache:
        return _cache
    with _lock:
        if not _cache:
            try:
                _cache["model"] = _load_pickle("catboost_fertilizer_model.pkl")
                _cache["input_columns"] = _load_pickle("fertilizer_input_columns.pkl")
                _cache["cat_features"] = _load_pickle("fertilizer_cat_features.pkl")
                _cache["cat_columns"] = _load_pickle("fertilizer_categorical_columns.pkl")
            except ModelNotAvailableError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to load fertilizer recommendation models")
                raise ModelNotAvailableError(str(exc)) from exc
    return _cache


def normalize_season(value):
    return SEASON_ALIASES.get(value.strip().lower(), value)


def predict_fertilizer(soil_type, soil_ph, nitrogen_level, phosphorus_level, potassium_level,
                        temperature, humidity, crop_type, crop_growth_stage, season,
                        irrigation_type, previous_crop):
    try:
        models = _get_models()
    except ModelNotAvailableError as exc:
        return {"success": False, "error": f"Fertilizer recommendation model is currently unavailable: {exc}"}

    try:
        import pandas as pd

        npk_imputed = False
        if nitrogen_level in (None, ""):
            nitrogen_level = DEFAULT_NITROGEN
            npk_imputed = True
        if phosphorus_level in (None, ""):
            phosphorus_level = DEFAULT_PHOSPHORUS
            npk_imputed = True
        if potassium_level in (None, ""):
            potassium_level = DEFAULT_POTASSIUM
            npk_imputed = True

        row = {
            "Soil_Type": str(soil_type),
            "Soil_pH": float(soil_ph),
            "Nitrogen_Level": float(nitrogen_level),
            "Phosphorus_Level": float(phosphorus_level),
            "Potassium_Level": float(potassium_level),
            "Temperature": float(temperature),
            "Humidity": float(humidity),
            "Crop_Type": str(crop_type),
            "Crop_Growth_Stage": str(crop_growth_stage),
            "Season": normalize_season(str(season)),
            "Irrigation_Type": str(irrigation_type),
            "Previous_Crop": str(previous_crop),
        }

        input_columns = models["input_columns"]
        df = pd.DataFrame([[row[col] for col in input_columns]], columns=input_columns)

        model = models["model"]
        raw_pred = model.predict(df)
        # CatBoost predict() may return a 2D array like [["Urea"]] or [0]
        value = raw_pred
        while hasattr(value, "__len__") and not isinstance(value, str) and len(value) == 1:
            value = value[0]

        fertilizer_name = str(value)
        # If the model predicted a numeric class index, map it via classes_ when available
        classes_attr = getattr(model, "classes_", None)
        if fertilizer_name.replace(".", "", 1).replace("-", "", 1).isdigit() and classes_attr is not None:
            try:
                idx = int(float(fertilizer_name))
                fertilizer_name = str(classes_attr[idx])
            except (ValueError, IndexError):
                pass

        return {
            "success": True,
            "error": None,
            "npk_imputed": npk_imputed,
            "fertilizer": fertilizer_name,
        }
    except Exception:
        logger.exception("Fertilizer prediction failed")
        return {"success": False, "error": "We couldn't generate a fertilizer recommendation from these inputs. Please check your values and try again."}
