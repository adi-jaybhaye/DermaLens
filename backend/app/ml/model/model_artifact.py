import hashlib
import logging
from pathlib import Path
from typing import Dict, Any

from app.config.settings import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_NAME = "EfficientNet-B0"
MODEL_VERSION = "efficientnet_b0_v1"
MODEL_CHECKSUM = "ba123334b476a24b710a78000a70b1d6dcc44ee100664673d6e61ed3d0827412"
NUM_CLASSES = 8
CLASS_NAMES = [
    "Redness",
    "dark spots",
    "inflammatory acne",
    "non inflammatory acne black heads",
    "non inflammatory acne white heads",
    "pigmentation",
    "pores",
    "wrinkles",
]


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_model_checksum(file_path: Path, expected_sha256: str = MODEL_CHECKSUM) -> bool:
    """Verify the integrity of the model weights file against expected checksum."""
    if not file_path.exists():
        return False
    actual_hash = compute_sha256(file_path)
    return actual_hash.lower() == expected_sha256.lower()


def resolve_model_artifact_path() -> Path:
    """Deterministically resolve and verify the production EfficientNet-B0 checkpoint.

    Resolution Priority:
    1. Explicit configured MODEL_PATH from settings
    2. Container deployment path: /app/models/efficientnet_b0_skin_concerns.pth
    3. Project models directory: models/efficientnet_b0_skin_concerns.pth
    4. Training artifacts directory: training/models/efficientnet_b0_skin_concerns.pth

    Enforcement:
    - If no candidate exists: raises FileNotFoundError.
    - If a candidate file exists but its SHA-256 does NOT match expected checksum:
      raises RuntimeError immediately (FAIL CLOSED).
    - Silent fallback to unverified or corrupted model weights is strictly prohibited.
    """
    expected_checksum = (settings.model_checksum or MODEL_CHECKSUM).strip().lower()

    candidates = []
    configured = Path(settings.model_path)
    if configured.is_absolute():
        candidates.append(configured)
    else:
        candidates.append(BASE_DIR / settings.model_path)

    candidates.extend([
        Path("/app/models/efficientnet_b0_skin_concerns.pth"),
        BASE_DIR / "models" / "efficientnet_b0_skin_concerns.pth",
        BASE_DIR / "training" / "models" / "efficientnet_b0_skin_concerns.pth",
    ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            actual_checksum = compute_sha256(candidate).lower()
            if actual_checksum == expected_checksum:
                logger.info(f"Loaded verified EfficientNet-B0 model artifact from: {candidate} (SHA-256 verified)")
                return candidate
            else:
                raise RuntimeError(
                    f"CRITICAL INTEGRITY FAILURE: EfficientNet-B0 model artifact at '{candidate}' "
                    f"failed SHA-256 checksum verification. Expected {expected_checksum}, "
                    f"got {actual_checksum}. Startup aborted to prevent unverified model execution."
                )

    raise FileNotFoundError(
        f"CRITICAL: EfficientNet-B0 model artifact not found. Checked: {[str(c) for c in candidates]}. "
        "In production, place 'efficientnet_b0_skin_concerns.pth' at /app/models/ or configure MODEL_PATH. "
        "Silent fake-model fallback is prohibited."
    )


def get_model_metadata() -> Dict[str, Any]:
    """Return verified metadata and methodology context for the active model."""
    return {
        "name": MODEL_NAME,
        "version": MODEL_VERSION,
        "expected_checksum": MODEL_CHECKSUM,
        "num_classes": NUM_CLASSES,
        "classes": CLASS_NAMES,
        "validation_accuracy": 0.9289,
        "evaluation_split_note": (
            "Evaluated on a deterministic 20% random validation split (seed 42, N=844 images) "
            "of the skin concerns dataset. Not clinical or population-level accuracy."
        ),
        "region_level_note": (
            "Regional facial crops represent prototype visual localization inference, "
            "not independently validated per-region performance."
        ),
        "skin_type_note": (
            "Skin-type classification is unavailable because accurate sebum and hydration "
            "metrics require biophysical contact probes (Sebumeter/Corneometer) not derivable from 2D photos."
        ),
    }
