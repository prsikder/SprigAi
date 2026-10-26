"""Quick verification that fixed Django service matches notebook inference."""
import io
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import mobilenet_v3_small

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "ai_models" / "disease_detection"


def notebook_predict(image_bytes: bytes):
    with open(MODEL_DIR / "class_names.json", encoding="utf-8") as f:
        class_names = json.load(f)
    checkpoint = torch.load(MODEL_DIR / "crop_disease_model.pth", map_location="cpu")
    model = mobilenet_v3_small(weights=None)
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, checkpoint["num_classes"])
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    transform = transforms.Compose([
        transforms.Resize((checkpoint["img_size"], checkpoint["img_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=checkpoint["mean"], std=checkpoint["std"]),
    ])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)
    top_prob, top_idx = torch.max(probs, 1)
    return class_names[str(top_idx.item())], round(float(top_prob.item()) * 100, 2)


def django_predict(image_bytes: bytes):
    sys.path.insert(0, str(ROOT))
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="debug-only",
            INSTALLED_APPS=["core"],
            ALLOWED_IMAGE_EXTENSIONS=["jpg", "jpeg", "png", "webp"],
            MAX_UPLOAD_SIZE_MB=20,
        )

    from core.services.image_model_service import ImageClassifierService

    class FakeUpload(io.BytesIO):
        name = "test.jpg"

        @property
        def size(self):
            return self.getbuffer().nbytes

    upload = FakeUpload(image_bytes)
    service = ImageClassifierService(
        name="verify",
        weights_path=MODEL_DIR / "crop_disease_model.pth",
        class_names_path=MODEL_DIR / "class_names.json",
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
        image_size=224,
    )
    result = service.predict(upload, top_k=5)
    if not result["success"]:
        raise RuntimeError(result["error"])
    return result["predicted_class"], result["confidence"]


def main():
    rng = np.random.RandomState(42)
    image = Image.fromarray(rng.randint(0, 255, (300, 400, 3), dtype=np.uint8))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")

    image_bytes = buf.getvalue()

    nb_label, nb_conf = notebook_predict(image_bytes)
    dj_label, dj_conf = django_predict(image_bytes)

    print("Notebook:", nb_label, f"{nb_conf:.2f}%")
    print("Django  :", dj_label, f"{dj_conf:.2f}%")
    if nb_label == dj_label and abs(nb_conf - dj_conf) < 0.05:
        print("PASS: predictions match")
        return 0
    print("FAIL: predictions differ")
    return 1


if __name__ == "__main__":
    sys.exit(main())
