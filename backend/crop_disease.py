import json
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any
import warnings

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from .disease_guidance import PLANTVILLAGE_CLASSES, guidance_for


LOGGER = logging.getLogger(__name__)
IMAGE_SIZE = 224
MAX_IMAGE_PIXELS = 25_000_000
DEFAULT_MODEL_DIR = Path(__file__).with_name("models") / "plant_disease_mobilenetv2"
SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}


class ModelUnavailableError(RuntimeError):
    pass


class UnsupportedImageError(ValueError):
    pass


class InvalidLeafImageError(ValueError):
    pass


class ImageTooLargeError(ValueError):
    pass


@dataclass(frozen=True)
class DiseaseModel:
    model: Any
    metadata: dict[str, Any]


def decode_leaf_image(content: bytes, content_type: str) -> np.ndarray:
    expected_format = SUPPORTED_IMAGE_TYPES.get(content_type)
    if expected_format is None:
        raise UnsupportedImageError("Upload a JPG, PNG or WebP image.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as image:
                if image.format != expected_format:
                    raise UnsupportedImageError(
                        "Image contents do not match the selected image format."
                    )
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ImageTooLargeError(
                        "Image dimensions are too large to process safely."
                    )
                image.verify()
            with Image.open(BytesIO(content)) as image:
                image.load()
                oriented = ImageOps.exif_transpose(image)
                resized = oriented.convert("RGB").resize(
                    (IMAGE_SIZE, IMAGE_SIZE),
                    Image.Resampling.BILINEAR,
                )
                return np.asarray(resized, dtype=np.float32)
    except (UnsupportedImageError, ImageTooLargeError):
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
    ) as error:
        raise InvalidLeafImageError(
            "The uploaded file is not a valid, supported image."
        ) from error


def _configured_model_dir() -> Path:
    configured = os.getenv("FASALSETU_DISEASE_MODEL_DIR")
    return Path(configured).expanduser() if configured else DEFAULT_MODEL_DIR


def get_disease_model() -> DiseaseModel | None:
    model_dir = _configured_model_dir()
    model_path = model_dir / "model.keras"
    metadata_path = model_dir / "metadata.json"

    if not model_path.exists() and not metadata_path.exists():
        return None
    if not model_path.is_file() or not metadata_path.is_file():
        raise ModelUnavailableError(
            "The configured crop model is incomplete; expected model.keras and metadata.json."
        )

    try:
        return _load_disease_model(str(model_path.resolve()), str(metadata_path.resolve()))
    except ModelUnavailableError:
        raise
    except Exception as error:
        LOGGER.exception("Could not load the configured crop disease model.")
        raise ModelUnavailableError(
            "The configured crop disease model could not be loaded. Check the backend logs."
        ) from error


@lru_cache(maxsize=2)
def _load_disease_model(model_path: str, metadata_path: str) -> DiseaseModel:
    try:
        import tensorflow as tf
    except ImportError as error:
        raise ModelUnavailableError(
            "TensorFlow is not installed. Install the optional requirements-ml.txt dependencies."
        ) from error

    with open(metadata_path, encoding="utf-8") as file:
        metadata = json.load(file)

    classes = metadata.get("classes")
    if (
        metadata.get("architecture") != "MobileNetV2"
        or metadata.get("image_size") != IMAGE_SIZE
        or metadata.get("preprocessing") != "internal_mobilenet_v2_minus1_to_1"
        or not isinstance(classes, list)
        or not all(isinstance(label, str) and label for label in classes)
        or len(classes) != len(PLANTVILLAGE_CLASSES)
        or len(set(classes)) != len(PLANTVILLAGE_CLASSES)
        or set(classes) != set(PLANTVILLAGE_CLASSES)
        or metadata.get("dataset") != "PlantVillage"
        or not isinstance(metadata.get("test_metrics"), dict)
        or not isinstance(metadata["test_metrics"].get("accuracy"), (int, float))
        or not 0 <= metadata["test_metrics"]["accuracy"] <= 1
    ):
        raise ModelUnavailableError("The configured model metadata is invalid or incompatible.")

    model = tf.keras.models.load_model(model_path, compile=False, safe_mode=True)
    output_shape = model.output_shape
    if (
        isinstance(output_shape, list)
        or not output_shape
        or output_shape[-1] != len(classes)
    ):
        raise ModelUnavailableError(
            "The configured model output does not match the class names in metadata.json."
        )
    return DiseaseModel(model=model, metadata=metadata)


def classify_leaf(image: np.ndarray, bundle: DiseaseModel, language: str = "en") -> dict[str, Any]:
    try:
        output = bundle.model.predict(np.expand_dims(image, axis=0), verbose=0)
        probabilities = np.asarray(output, dtype=np.float64).reshape(-1)
    except Exception as error:
        LOGGER.exception("Crop disease model inference failed.")
        raise ModelUnavailableError(
            "Crop disease inference failed. Check the backend logs; no result was returned."
        ) from error

    classes = bundle.metadata["classes"]
    if (
        probabilities.size != len(classes)
        or not np.isfinite(probabilities).all()
        or np.any(probabilities < 0)
        or np.any(probabilities > 1)
        or not np.isclose(probabilities.sum(), 1.0, atol=0.02)
    ):
        raise ModelUnavailableError(
            "The configured model returned invalid class scores; no result was returned."
        )

    index = int(np.argmax(probabilities))
    confidence = float(probabilities[index])
    class_name = classes[index]
    crop, _, disease = class_name.partition("___")
    uncertain = confidence < 0.60
    if language == "hi":
        confidence_warning = (
            "मॉडल स्कोर कम है: परिणाम विशेष रूप से अनिश्चित है; स्थानीय कृषि विशेषज्ञ से पुष्टि करें।"
            if uncertain
            else "मॉडल स्कोर कैलिब्रेटेड संभावना या सटीकता की गारंटी नहीं है। खेत की स्थिति प्रशिक्षण तस्वीरों से अलग हो सकती है।"
        )
        disclaimer = (
            "तस्वीर का वर्गीकरण केवल सहायक संकेत है, खेत में रोग का निदान नहीं। कोई कदम उठाने से पहले स्थानीय कृषि विशेषज्ञ "
            "या KVK से पुष्टि करें। कीटनाशक की मात्रा नहीं दी जाती।"
        )
    else:
        confidence_warning = (
            "Low model score: treat this result as especially uncertain and seek local expert confirmation."
            if uncertain
            else "Model confidence is not a calibrated probability or a guarantee of accuracy. Field conditions may differ from training images."
        )
        disclaimer = (
            "Image classification is an aid, not a field diagnosis. Confirm with a local "
            "agriculture expert or KVK before taking action. No pesticide dosage is provided."
        )
    return {
        "status": "prediction",
        "prediction": {
            "class_name": class_name,
            "crop": crop.replace("_", " "),
            "disease": disease.replace("_", " ").strip(),
            "confidence": round(confidence, 4),
            "uncertain": uncertain,
        },
        "confidence_warning": confidence_warning,
        "guidance": guidance_for(class_name, language),
        "model": {
            "name": bundle.metadata.get("model_name", "MobileNetV2 plant disease classifier"),
            "architecture": bundle.metadata["architecture"],
            "dataset": bundle.metadata.get("dataset", "Not specified"),
            "class_count": len(classes),
        },
        "disclaimer": disclaimer,
    }
