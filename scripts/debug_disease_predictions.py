#!/usr/bin/env python
"""
Compare Django disease-detection inference against Crop_disease_trained.ipynb.

Usage:
    python scripts/debug_disease_predictions.py path/to/image1.jpg path/to/image2.jpg

Optional environment variables:
    DISEASE_MODEL_DIR   - defaults to ai_models/disease_detection
    PREDICTION_DEBUG=1  - enable verbose service logging
"""
from __future__ import annotations

import io
import json
import sys
from io import BytesIO
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import mobilenet_v3_small

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = Path(__import__("os").getenv("DISEASE_MODEL_DIR", ROOT / "ai_models" / "disease_detection"))
MODEL_PATH = MODEL_DIR / "crop_disease_model.pth"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"
METRICS_PATH = MODEL_DIR / "metrics.json"


class FakeUpload(io.BytesIO):
    def __init__(self, path: Path):
        super().__init__(path.read_bytes())
        self.name = path.name

    @property
    def size(self):
        return self.getbuffer().nbytes


def load_notebook_predictor():
    with open(CLASS_NAMES_PATH, encoding="utf-8") as f:
        class_names_json = json.load(f)

    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    model = mobilenet_v3_small(weights=None)
    model.classifier[-1] = nn.Linear(
        model.classifier[-1].in_features,
        checkpoint["num_classes"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((checkpoint["img_size"], checkpoint["img_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=checkpoint["mean"], std=checkpoint["std"]),
    ])
    return model, transform, class_names_json, checkpoint


def predict_notebook(image_path: Path, model, transform, class_names_json):
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)
    top5_prob, top5_idx = torch.topk(probs, k=min(5, probs.shape[1]))
    rows = []
    for prob, idx in zip(top5_prob[0], top5_idx[0]):
        rows.append((class_names_json[str(idx.item())], float(prob.item()) * 100))
    return rows


def predict_django(image_path: Path):
    sys.path.insert(0, str(ROOT))
    import django
    from django.conf import settings as django_settings

    if not django_settings.configured:
        django_settings.configure(
            DEBUG=True,
            SECRET_KEY="debug-only",
            INSTALLED_APPS=["disease_detection", "core"],
            DISEASE_MODEL_DIR=MODEL_DIR,
            ALLOWED_IMAGE_EXTENSIONS=["jpg", "jpeg", "png", "webp", ".jpg", ".jpeg", ".png", ".webp"],
            MAX_UPLOAD_SIZE_MB=20,
            AI_MODELS_DIR=ROOT / "ai_models",
        )
        django.setup()

    from disease_detection.services.disease_service import predict_disease

    upload = FakeUpload(image_path)
    return predict_disease(upload)


def main(argv):
    if len(argv) < 2:
        print("Provide at least one image path.")
        print(__doc__)
        return 1

    if not MODEL_PATH.exists():
        print(f"Missing model: {MODEL_PATH}")
        return 1

    metrics = {}
    if METRICS_PATH.exists():
        with open(METRICS_PATH, encoding="utf-8") as f:
            metrics = json.load(f)

    model, transform, class_names_json, checkpoint = load_notebook_predictor()
    print("=" * 72)
    print("Model path     :", MODEL_PATH)
    print("Class names    :", list(class_names_json.values()))
    print("Metrics image  :", metrics.get("image_size", checkpoint.get("img_size")))
    print("Metrics mean   :", metrics.get("mean", checkpoint.get("mean")))
    print("Metrics std    :", metrics.get("std", checkpoint.get("std")))
    print("=" * 72)

    mismatches = 0
    for image_arg in argv[1:]:
        image_path = Path(image_arg)
        if not image_path.exists():
            print(f"\n[SKIP] Missing image: {image_path}")
            continue

        nb_top = predict_notebook(image_path, model, transform, class_names_json)
        dj_result = predict_django(image_path)

        print(f"\nImage: {image_path.name}")
        print("Notebook top-5:")
        for label, conf in nb_top:
            print(f"  {label:35s} {conf:6.2f}%")

        if not dj_result.get("success"):
            print("Django ERROR:", dj_result.get("error"))
            mismatches += 1
            continue

        print("Django top-5:")
        for item in dj_result["top_predictions"]:
            print(f"  {item['label']:35s} {item['confidence']:6.2f}%")

        nb_best = nb_top[0]
        dj_best = (dj_result["predicted_class"], dj_result["confidence"])
        match = nb_best[0] == dj_best[0] and abs(nb_best[1] - dj_best[1]) < 0.05
        status = "MATCH" if match else "MISMATCH"
        print(f"Result: {status} | notebook={nb_best[0]} ({nb_best[1]:.2f}%) | django={dj_best[0]} ({dj_best[1]:.2f}%)")
        if not match:
            mismatches += 1

    print("\n" + "=" * 72)
    if mismatches:
        print(f"Finished with {mismatches} mismatch(es).")
        return 1
    print("All compared images match notebook predictions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
