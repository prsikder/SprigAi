#!/usr/bin/env python
"""
Validate soil classification deployment against the training notebook.

Loads one sample image from each of the six soil classes and compares
notebook-style inference with the Django ImageClassifierService.

Usage:
    python scripts/debug_soil_predictions.py
"""
from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import transforms
from torchvision.models import mobilenet_v3_small

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "ai_models" / "soil_classification"
DATASET = ROOT / "dataset" / "soil dataset"
CLASSES = [
    "Alluvial_Soil",
    "Arid_Soil",
    "Black_Soil",
    "Laterite_Soil",
    "Red_Soil",
    "Yellow_Soil",
]


class FakeUpload(io.BytesIO):
    def __init__(self, path: Path):
        super().__init__(path.read_bytes())
        self.name = path.name

    @property
    def size(self):
        return self.getbuffer().nbytes


def sample_image(class_name: str) -> Path:
    return next((DATASET / class_name).glob("*"))


def load_notebook_predictor():
    with open(MODEL_DIR / "class_names.json", encoding="utf-8") as f:
        class_names_json = json.load(f)

    checkpoint = torch.load(
        MODEL_DIR / "soil_classifier.pth",
        map_location="cpu",
        weights_only=False,
    )
    state_dict = checkpoint["model_state_dict"]
    class_names = list(checkpoint["class_names"])

    model = mobilenet_v3_small(weights=None)
    model.classifier[-1] = nn.Linear(
        model.classifier[-1].in_features,
        checkpoint["num_classes"],
    )
    model.load_state_dict(state_dict, strict=True)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((checkpoint["img_size"], checkpoint["img_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=checkpoint["mean"], std=checkpoint["std"]),
    ])
    return model, transform, class_names, class_names_json, checkpoint


def predict_notebook(path: Path, model, transform, class_names):
    image = ImageOps.exif_transpose(Image.open(path).convert("RGB"))
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]
    top_probs, top_idxs = torch.topk(probs, k=5)
    return [
        (class_names[idx], round(float(prob) * 100, 2))
        for prob, idx in zip(top_probs.tolist(), top_idxs.tolist())
    ]


def predict_django(path: Path):
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sprigai_project.settings")
    import django

    django.setup()

    from soil_classification.services import soil_service

    soil_service._predictor = None
    return soil_service.predict_soil(FakeUpload(path))


def main():
    if not (MODEL_DIR / "soil_classifier.pth").exists():
        print(f"Missing model: {MODEL_DIR / 'soil_classifier.pth'}")
        return 1

    model, transform, class_names, class_names_json, checkpoint = load_notebook_predictor()
    print("=" * 72)
    print("Model path     :", MODEL_DIR / "soil_classifier.pth")
    print("Class names    :", class_names)
    print("Metrics image  :", checkpoint.get("img_size"))
    print("Metrics mean   :", checkpoint.get("mean"))
    print("Metrics std    :", checkpoint.get("std"))
    print("=" * 72)

    mismatches = 0
    for expected in CLASSES:
        path = sample_image(expected)
        nb_top = predict_notebook(path, model, transform, class_names)
        dj_result = predict_django(path)

        print(f"\nImage: {path.name} | expected={expected}")
        print("Notebook top-5:")
        for label, conf in nb_top:
            print(f"  {label:16s} {conf:6.2f}%")

        if not dj_result.get("success"):
            print("Django ERROR:", dj_result.get("error"))
            mismatches += 1
            continue

        print("Django top-5:")
        for item in dj_result["top_predictions"]:
            print(f"  {item['label']:16s} {item['confidence']:6.2f}%")

        nb_best = nb_top[0]
        dj_best = (dj_result["predicted_class"], dj_result["confidence"])
        match = nb_best[0] == dj_best[0] and abs(nb_best[1] - dj_best[1]) < 0.05
        status = "MATCH" if match else "MISMATCH"
        print(f"Result: {status} | notebook={nb_best[0]} ({nb_best[1]:.2f}%) | django={dj_best[0]} ({dj_best[1]:.2f}%)")
        if nb_best[0] != expected:
            print(f"  NOTE: notebook top-1 differs from folder label ({expected})")
        if not match:
            mismatches += 1

    print("\n" + "=" * 72)
    if mismatches:
        print(f"Finished with {mismatches} mismatch(es).")
        return 1
    print("All six classes match notebook predictions in Django.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
