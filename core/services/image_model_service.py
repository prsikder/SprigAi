"""
Shared PyTorch image-model inference service.

Both Crop Disease Detection and Soil Classification use a MobileNetV3-Small
classifier (see ai_models/*/metrics.json -> "model": "MobileNetV3 Small",
"image_size": 224, ImageNet-style mean/std normalization). This module
centralizes model loading, preprocessing, and safe inference so neither
app has to duplicate messy ML/torch code inside its views.

Usage:
    predictor = ImageClassifierService(
        weights_path=..., class_names_path=..., num_classes=16,
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], image_size=224,
    )
    result = predictor.predict(uploaded_file)
"""
import io
import json
import logging
import os
import threading

from django.conf import settings

logger = logging.getLogger("sprigai")

_PREDICTION_DEBUG = os.getenv("PREDICTION_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


class ModelNotAvailableError(Exception):
    pass


class InvalidImageError(Exception):
    pass


def _extension_allowed(ext):
    normalized = ext.lower().lstrip(".")
    allowed = {item.lower().lstrip(".") for item in settings.ALLOWED_IMAGE_EXTENSIONS}
    return normalized in allowed


def validate_image_file(django_file):
    """Validate extension and size before doing any AI processing."""
    ext = os.path.splitext(django_file.name)[1].lower()
    if not _extension_allowed(ext):
        raise InvalidImageError(
            f"Unsupported file type '{ext}'. Please upload JPG, JPEG, PNG, or WEBP."
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if django_file.size > max_bytes:
        raise InvalidImageError(
            f"File is too large ({django_file.size / (1024*1024):.1f}MB). "
            f"Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB."
        )
    try:
        from PIL import Image
        django_file.seek(0)
        img = Image.open(django_file)
        img.verify()
        django_file.seek(0)
    except Exception as exc:
        raise InvalidImageError("The uploaded file is not a valid image.") from exc


_CHECKPOINT_METADATA_KEYS = frozenset({
    "class_names",
    "class_to_idx",
    "img_size",
    "image_size",
    "mean",
    "std",
    "model_name",
    "num_classes",
    "label_smoothing",
})


def _validate_state_dict(state_dict):
    """Reject checkpoints that were passed to load_state_dict without unpacking."""
    if not isinstance(state_dict, dict) or not state_dict:
        raise ModelNotAvailableError("Checkpoint state_dict is empty or invalid.")

    bad_keys = [key for key in state_dict if key in _CHECKPOINT_METADATA_KEYS]
    if bad_keys:
        raise ModelNotAvailableError(
            "Checkpoint weights were not extracted correctly. "
            f"Found metadata keys inside state_dict: {bad_keys}. "
            "Expected checkpoint['model_state_dict']."
        )


def _extract_state_dict(checkpoint):
    """
    Match Soil_Classification / Crop_disease notebook checkpoint layout:
      torch.save({"model_state_dict": ..., "num_classes": ..., ...}, path)
    Also accept a bare state_dict or legacy {"state_dict": ...} wrappers.
    """
    import torch.nn as nn

    if isinstance(checkpoint, nn.Module):
        return checkpoint, {}

    if not isinstance(checkpoint, dict):
        return checkpoint, {}

    metadata = {
        key: value
        for key, value in checkpoint.items()
        if key not in {"model_state_dict", "state_dict"}
    }
    if "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    elif "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    elif any(key in checkpoint for key in _CHECKPOINT_METADATA_KEYS):
        raise ModelNotAvailableError(
            "Checkpoint file contains metadata but no 'model_state_dict' key."
        )
    else:
        state_dict = checkpoint
        metadata = {}

    if not isinstance(state_dict, nn.Module):
        _validate_state_dict(state_dict)
    return state_dict, metadata


def _load_class_names(raw, metadata, num_classes):
    """
    Preserve training label order.
    Prefer checkpoint metadata, then class_names.json (dict or list).
    """
    checkpoint_names = metadata.get("class_names")
    if isinstance(checkpoint_names, list) and len(checkpoint_names) == num_classes:
        return list(checkpoint_names), {"ordered": checkpoint_names}

    if isinstance(raw, list):
        if len(raw) != num_classes:
            raise ModelNotAvailableError(
                f"class_names.json list length={len(raw)} does not match num_classes={num_classes}."
            )
        return list(raw), {str(i): name for i, name in enumerate(raw)}

    if not isinstance(raw, dict):
        raise ModelNotAvailableError("class_names.json must be a dict or list.")

    class_names = [raw[str(i)] for i in range(len(raw))]
    if len(class_names) != num_classes:
        raise ModelNotAvailableError(
            f"class_names.json length={len(class_names)} does not match num_classes={num_classes}."
        )
    return class_names, raw


def _open_rgb_image(file_bytes):
    from PIL import Image, ImageOps

    image = Image.open(io.BytesIO(file_bytes))
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


class ImageClassifierService:
    """
    Lazily-loaded, thread-safe MobileNetV3-Small classifier wrapper.
    Falls back gracefully (never raises to the caller's caller) via .predict().
    """

    def __init__(self, name, weights_path, class_names_path, mean=None, std=None, image_size=224):
        self.name = name
        self.weights_path = weights_path
        self.class_names_path = class_names_path
        self.mean = mean or [0.485, 0.456, 0.406]
        self.std = std or [0.229, 0.224, 0.225]
        self.image_size = image_size
        self._lock = threading.Lock()
        self._model = None
        self._class_names = None
        self._class_names_raw = None

    def _load(self):
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            if not self.weights_path.exists():
                raise ModelNotAvailableError(
                    f"{self.name} model file is missing. Expected at: {self.weights_path}"
                )
            if not self.class_names_path.exists():
                raise ModelNotAvailableError(
                    f"{self.name} class-name file is missing. Expected at: {self.class_names_path}"
                )
            try:
                import torch
                import torch.nn as nn
                from torchvision.models import mobilenet_v3_small

                with open(self.class_names_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                checkpoint = torch.load(self.weights_path, map_location="cpu")
                state_dict, metadata = _extract_state_dict(checkpoint)

                num_classes = metadata.get("num_classes")
                if num_classes is None:
                    if isinstance(raw, list):
                        num_classes = len(raw)
                    else:
                        num_classes = len(raw)
                num_classes = int(num_classes)

                class_names, class_names_raw = _load_class_names(raw, metadata, num_classes)

                if metadata.get("mean") is not None:
                    self.mean = list(metadata["mean"])
                if metadata.get("std") is not None:
                    self.std = list(metadata["std"])
                image_size = metadata.get("img_size", metadata.get("image_size"))
                if image_size is not None:
                    self.image_size = int(image_size)

                if isinstance(state_dict, nn.Module):
                    model = state_dict
                else:
                    model = mobilenet_v3_small(weights=None)
                    in_features = model.classifier[-1].in_features
                    model.classifier[-1] = nn.Linear(in_features, num_classes)
                    load_result = model.load_state_dict(state_dict, strict=True)
                    if load_result.missing_keys or load_result.unexpected_keys:
                        raise ModelNotAvailableError(
                            f"Weight load mismatch (missing={load_result.missing_keys}, "
                            f"unexpected={load_result.unexpected_keys})"
                        )
                model.eval()

                self._model = model
                self._class_names = class_names
                self._class_names_raw = class_names_raw

                logger.info(
                    "%s: loaded model from %s | classes=%d | image_size=%d | mean=%s | std=%s",
                    self.name,
                    self.weights_path,
                    len(class_names),
                    self.image_size,
                    self.mean,
                    self.std,
                )
                logger.debug(
                    "%s: class_names=%s | checkpoint_metadata_keys=%s",
                    self.name,
                    class_names,
                    sorted(metadata.keys()),
                )
            except ModelNotAvailableError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("%s: failed to load model", self.name)
                raise ModelNotAvailableError(str(exc)) from exc

    def predict(self, django_file, top_k=3):
        """
        Returns a dict:
          {success, error, predicted_class, confidence, top_predictions: [{label, confidence}, ...]}
        """
        try:
            validate_image_file(django_file)
        except InvalidImageError as exc:
            return {"success": False, "error": str(exc)}

        try:
            self._load()
        except ModelNotAvailableError as exc:
            return {"success": False, "error": f"{self.name} is currently unavailable: {exc}"}

        try:
            import torch
            from torchvision import transforms

            django_file.seek(0)
            image = _open_rgb_image(django_file.read())

            # Match Soil_Classification_MobileNetV3_Small_Kaggle.ipynb eval_transform.
            preprocess = transforms.Compose([
                transforms.Resize((self.image_size, self.image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.mean, std=self.std),
            ])
            tensor = preprocess(image).unsqueeze(0)

            with torch.no_grad():
                logits = self._model(tensor)
                probs = torch.nn.functional.softmax(logits, dim=1)[0]

            top_k = min(top_k, len(self._class_names))
            top_probs, top_idxs = torch.topk(probs, k=top_k)
            top_predictions = [
                {"label": self._class_names[idx], "confidence": round(float(p) * 100, 2)}
                for p, idx in zip(top_probs.tolist(), top_idxs.tolist())
            ]
            best_idx = top_idxs[0].item()
            best = top_predictions[0]

            if _PREDICTION_DEBUG or settings.DEBUG:
                logger.info(
                    "%s prediction debug | file=%s | tensor_shape=%s | tensor_min=%.4f | tensor_max=%.4f",
                    self.name,
                    getattr(django_file, "name", "<unknown>"),
                    tuple(tensor.shape),
                    float(tensor.min()),
                    float(tensor.max()),
                )
                logger.info(
                    "%s prediction debug | pred_idx=%d | pred_class=%s | confidence=%.2f%%",
                    self.name,
                    best_idx,
                    best["label"],
                    best["confidence"],
                )
                logger.info(
                    "%s prediction debug | top-%d=%s",
                    self.name,
                    top_k,
                    top_predictions,
                )
                logger.debug(
                    "%s prediction debug | softmax_probs=%s",
                    self.name,
                    [round(float(p), 6) for p in probs.tolist()],
                )

            return {
                "success": True,
                "error": None,
                "predicted_class": best["label"],
                "confidence": best["confidence"],
                "top_predictions": top_predictions,
            }
        except Exception:
            logger.exception("%s: inference failed", self.name)
            return {"success": False, "error": "We couldn't process this image. Please try a different photo."}
