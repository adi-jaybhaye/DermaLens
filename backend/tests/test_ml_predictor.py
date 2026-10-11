import io
import pytest
import numpy as np
from PIL import Image

from app.ml.model.efficientnet_predictor import get_predictor, predict_skin_concern
from app.ml.xai.gradcam import generate_gradcam
from app.config.settings import settings


@pytest.fixture(scope="module")
def sample_image_bytes():
    """Create a sample 224x224 RGB image with synthetic texture for testing."""
    arr = np.random.randint(50, 200, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_efficientnet_model_initialization():
    predictor = get_predictor()
    assert predictor is not None
    # Model must be in evaluation mode
    assert predictor.model.training is False

    # Verify exact 8 classes from Dataset A
    expected_classes = {
        "Redness",
        "dark spots",
        "inflammatory acne",
        "non inflammatory acne black heads",
        "non inflammatory acne white heads",
        "pigmentation",
        "pores",
        "wrinkles",
    }
    assert set(predictor.class_names) == expected_classes
    assert len(predictor.class_names) == 8


def test_skin_concern_inference_and_abstention(sample_image_bytes):
    result = predict_skin_concern(sample_image_bytes)

    assert result["success"] is True
    assert result["predicted_concern"] in {
        "Redness",
        "dark spots",
        "inflammatory acne",
        "non inflammatory acne black heads",
        "non inflammatory acne white heads",
        "pigmentation",
        "pores",
        "wrinkles",
    }
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["model_version"] == settings.model_version

    # Probabilities must sum to ~1.0
    probs = result["probabilities"]
    assert len(probs) == 8
    prob_sum = sum(probs.values())
    assert 0.99 <= prob_sum <= 1.01

    # Abstention / confidence status verification
    threshold = result["threshold_used"]
    assert threshold == settings.min_confidence_threshold
    if result["confidence"] >= threshold:
        assert result["is_confident"] is True
        assert result["confidence_status"] == "possible_pattern"
    else:
        assert result["is_confident"] is False
        assert result["confidence_status"] == "insufficient_confidence"


def test_gradcam_generation(sample_image_bytes):
    cam_result = generate_gradcam(sample_image_bytes)

    assert cam_result["success"] is True
    assert "heatmap_base64" in cam_result
    assert "overlay_base64" in cam_result
    assert len(cam_result["heatmap_base64"]) > 100
    assert len(cam_result["overlay_base64"]) > 100
    assert cam_result["predicted_concern"] is not None
