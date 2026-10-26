from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.services.image_model_service import ImageClassifierService, ModelNotAvailableError, _extract_state_dict
from django.conf import settings
from .services.soil_service import get_crop_suggestions, predict_soil


class SoilClassificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="farmer", password="StrongPass123!")
        self.client.login(username="farmer", password="StrongPass123!")

    def test_form_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("soil_classification:form"))
        self.assertEqual(resp.status_code, 302)

    def test_form_page_loads(self):
        resp = self.client.get(reverse("soil_classification:form"))
        self.assertEqual(resp.status_code, 200)

    def test_crop_suggestions_known_soil(self):
        crops = get_crop_suggestions("Alluvial_Soil")
        self.assertIn("Rice", crops)

    def test_crop_suggestions_unknown_soil(self):
        crops = get_crop_suggestions("Unknown_Soil")
        self.assertEqual(crops, [])

    def test_checkpoint_unpack_rejects_metadata_dict(self):
        fake_checkpoint = {
            "model_state_dict": {"features.0.0.weight": "ok"},
            "class_names": ["A"],
            "num_classes": 1,
        }
        state_dict, metadata = _extract_state_dict(fake_checkpoint)
        self.assertIn("features.0.0.weight", state_dict)
        self.assertEqual(metadata["num_classes"], 1)

        with self.assertRaises(ModelNotAvailableError):
            _extract_state_dict(
                {
                    "class_names": ["A"],
                    "num_classes": 1,
                    "mean": [0.1, 0.2, 0.3],
                }
            )

    def test_model_weights_load_strictly(self):
        service = ImageClassifierService(
            name="Soil Classification",
            weights_path=settings.SOIL_MODEL_DIR / "soil_classifier.pth",
            class_names_path=settings.SOIL_MODEL_DIR / "class_names.json",
        )
        service._load()
        self.assertEqual(len(service._class_names), 6)

    def test_predict_dataset_sample_not_random_yellow(self):
        sample = next((settings.BASE_DIR / "dataset" / "soil dataset" / "Arid_Soil").glob("*"))
        upload = SimpleUploadedFile(sample.name, sample.read_bytes(), content_type="image/jpeg")
        result = predict_soil(upload)
        self.assertTrue(result["success"])
        self.assertEqual(result["predicted_class"], "Arid_Soil")
        self.assertGreater(result["confidence"], 50)
