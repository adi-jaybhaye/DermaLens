import pytest
from pathlib import Path
from app.ml.model.model_artifact import (
    resolve_model_artifact_path,
    verify_model_checksum,
    compute_sha256,
    MODEL_CHECKSUM,
)
from app.config.settings import settings


def test_real_model_artifact_exists_and_checksum_valid():
    """Verify that the real production model artifact exists and strictly matches expected SHA-256."""
    artifact_path = resolve_model_artifact_path()
    assert artifact_path.exists()
    assert artifact_path.is_file()

    actual_checksum = compute_sha256(artifact_path)
    assert actual_checksum.lower() == MODEL_CHECKSUM.lower()
    assert verify_model_checksum(artifact_path) is True


def test_model_artifact_checksum_mismatch_fails_closed(monkeypatch, tmp_path):
    """Verify that any model checkpoint with an invalid/mismatched checksum raises RuntimeError (FAIL CLOSED)."""
    # Create a corrupted/tampered weights file
    corrupt_model = tmp_path / "corrupt_efficientnet.pth"
    corrupt_model.write_bytes(b"corrupted_or_tampered_model_weights_header")

    monkeypatch.setattr(settings, "model_path", str(corrupt_model))

    with pytest.raises(RuntimeError) as exc_info:
        resolve_model_artifact_path()

    assert "CRITICAL INTEGRITY FAILURE" in str(exc_info.value)
    assert "failed SHA-256 checksum verification" in str(exc_info.value)
    assert "Startup aborted" in str(exc_info.value)


def test_model_artifact_missing_fails(monkeypatch, tmp_path):
    """Verify that a completely missing model file raises FileNotFoundError."""
    non_existent = tmp_path / "missing_dir" / "non_existent_weights.pth"
    monkeypatch.setattr(settings, "model_path", str(non_existent))

    # Also override default fallback locations to prevent resolving local repository file
    from app.ml.model import model_artifact
    monkeypatch.setattr(model_artifact, "BASE_DIR", tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        resolve_model_artifact_path()

    assert "EfficientNet-B0 model artifact not found" in str(exc_info.value)

