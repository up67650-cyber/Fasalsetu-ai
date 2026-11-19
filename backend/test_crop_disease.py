import os
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image


TEST_DIRECTORY = tempfile.TemporaryDirectory()

from backend import main  # noqa: E402


def png_image() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 24), color=(74, 129, 58)).save(buffer, format="PNG")
    return buffer.getvalue()


def jpeg_image() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 24), color=(74, 129, 58)).save(buffer, format="JPEG")
    return buffer.getvalue()


class FakeModel:
    def __init__(self, scores: list[float]):
        self.scores = np.asarray([scores], dtype=np.float32)

    def predict(self, batch: np.ndarray, verbose: int = 0) -> np.ndarray:
        if batch.shape != (1, 224, 224, 3):
            raise AssertionError(f"Unexpected preprocessed input shape: {batch.shape}")
        return self.scores


class CropDiagnosisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.database_override = patch.object(
            main,
            "DATABASE_PATH",
            Path(TEST_DIRECTORY.name) / "test.sqlite3",
        )
        cls.database_override.start()
        cls.client_context = TestClient(main.app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_context.__exit__(None, None, None)
        cls.database_override.stop()
        TEST_DIRECTORY.cleanup()

    def test_status_reports_demo_mode_when_no_checkpoint_exists(self) -> None:
        with tempfile.TemporaryDirectory() as model_dir, patch.dict(
            os.environ, {"FASALSETU_DISEASE_MODEL_DIR": model_dir}
        ):
            response = self.client.get("/api/crop-diagnosis/status")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["available"])
        self.assertIn("No predictions", response.json()["message"])

    def test_rejects_unsupported_media_type(self) -> None:
        response = self.client.post(
            "/api/crop-diagnosis",
            files={"image": ("leaf.gif", b"GIF89a", "image/gif")},
        )
        self.assertEqual(response.status_code, 415)

    def test_rejects_corrupt_image_with_allowed_mime_type(self) -> None:
        response = self.client.post(
            "/api/crop-diagnosis",
            files={"image": ("leaf.png", b"\x89PNG\r\n\x1a\nnot-an-image", "image/png")},
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_bytes_that_do_not_match_declared_format(self) -> None:
        response = self.client.post(
            "/api/crop-diagnosis",
            files={"image": ("leaf.png", jpeg_image(), "image/png")},
        )
        self.assertEqual(response.status_code, 415)

    def test_rejects_uploads_over_ten_megabytes(self) -> None:
        response = self.client.post(
            "/api/crop-diagnosis",
            files={
                "image": (
                    "leaf.png",
                    b"x" * (10 * 1024 * 1024 + 1),
                    "image/png",
                )
            },
        )
        self.assertEqual(response.status_code, 413)

    def test_valid_image_returns_no_prediction_without_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as model_dir, patch.dict(
            os.environ, {"FASALSETU_DISEASE_MODEL_DIR": model_dir}
        ):
            response = self.client.post(
                "/api/crop-diagnosis",
                files={"image": ("leaf.png", png_image(), "image/png")},
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn("No prediction was made", response.json()["detail"])

    def test_inference_response_includes_class_score_guidance_and_warning(self) -> None:
        diagnoses_before = self.client.get("/api/dashboard/summary").json()["totals"]["diagnoses"]
        metadata = {
            "model_name": "Test-only response contract",
            "architecture": "MobileNetV2",
            "dataset": "PlantVillage",
            "classes": ["Tomato___Late_blight", "Tomato___healthy"],
        }
        bundle = SimpleNamespace(
            model=FakeModel([0.85, 0.15]),
            metadata=metadata,
        )
        with patch.object(main, "get_disease_model", return_value=bundle):
            response = self.client.post(
                "/api/crop-diagnosis",
                files={"image": ("leaf.png", png_image(), "image/png")},
            )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["prediction"]["class_name"], "Tomato___Late_blight")
        self.assertEqual(result["prediction"]["confidence"], 0.85)
        self.assertFalse(result["prediction"]["uncertain"])
        self.assertIn("not a calibrated probability", result["confidence_warning"])
        self.assertIn("symptoms", result["guidance"])
        self.assertIn("No pesticide dosage", result["disclaimer"])
        summary = self.client.get("/api/dashboard/summary").json()
        self.assertEqual(summary["totals"]["diagnoses"], diagnoses_before + 1)
        self.assertEqual(summary["latest_diagnosis"]["prediction"]["class_name"], "Tomato___Late_blight")

    def test_low_score_is_marked_uncertain(self) -> None:
        metadata = {
            "model_name": "Test-only response contract",
            "architecture": "MobileNetV2",
            "dataset": "PlantVillage",
            "classes": ["Tomato___Late_blight", "Tomato___healthy"],
        }
        bundle = SimpleNamespace(
            model=FakeModel([0.55, 0.45]),
            metadata=metadata,
        )
        with patch.object(main, "get_disease_model", return_value=bundle):
            response = self.client.post(
                "/api/crop-diagnosis",
                files={"image": ("leaf.png", png_image(), "image/png")},
            )
        self.assertTrue(response.json()["prediction"]["uncertain"])
        self.assertIn("especially uncertain", response.json()["confidence_warning"])

    def test_hindi_request_returns_hindi_guidance_and_safety_text(self) -> None:
        metadata = {
            "model_name": "Test-only response contract",
            "architecture": "MobileNetV2",
            "dataset": "PlantVillage",
            "classes": ["Tomato___Late_blight", "Tomato___healthy"],
        }
        bundle = SimpleNamespace(
            model=FakeModel([0.85, 0.15]),
            metadata=metadata,
        )
        with patch.object(main, "get_disease_model", return_value=bundle):
            response = self.client.post(
                "/api/crop-diagnosis?language=hi",
                files={"image": ("leaf.png", png_image(), "image/png")},
            )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["prediction"]["crop"], "Tomato")
        self.assertIn("पानी-जैसे अनियमित घाव", result["guidance"]["symptoms"])
        self.assertIn("मॉडल स्कोर कैलिब्रेटेड", result["confidence_warning"])
        self.assertIn("स्थानीय कृषि विशेषज्ञ", result["disclaimer"])
        self.assertIn("कीटनाशक की मात्रा नहीं दी जाती", result["disclaimer"])


if __name__ == "__main__":
    unittest.main()
