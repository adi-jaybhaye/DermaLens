from pathlib import Path
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

from app.config.settings import settings


BASE_DIR = Path(__file__).resolve().parents[3]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMAGE_SIZE = 224

TRANSFORM = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def resolve_model_path() -> Path:
    """Resolve model path from settings or fallback locations."""
    configured = Path(settings.model_path)
    if configured.is_absolute() and configured.exists():
        return configured

    # Relative to base directory
    candidate1 = BASE_DIR / settings.model_path
    if candidate1.exists():
        return candidate1

    candidate2 = BASE_DIR / "training" / "models" / "efficientnet_b0_skin_concerns.pth"
    if candidate2.exists():
        return candidate2

    candidate3 = BASE_DIR / "models" / "efficientnet_b0_skin_concerns.pth"
    if candidate3.exists():
        return candidate3

    raise FileNotFoundError(
        f"EfficientNet-B0 checkpoint not found at '{settings.model_path}'. "
        "Please ensure the model weights are placed in training/models/ or configure MODEL_PATH."
    )


class EfficientNetSkinConcernPredictor:

    def __init__(self):
        model_path = resolve_model_path()
        checkpoint = torch.load(
            model_path,
            map_location=DEVICE,
            weights_only=True,
        )

        self.class_names = checkpoint["class_names"]
        self.model = models.efficientnet_b0(weights=None)

        input_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(
            input_features,
            len(self.class_names),
        )

        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(DEVICE)
        self.model.eval()

    def predict(self, image_bytes: bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
            predicted_index = torch.argmax(probabilities).item()

        predicted_class = self.class_names[predicted_index]
        confidence = float(probabilities[predicted_index].item())

        probabilities_dict = {
            class_name: round(float(prob.item()), 4)
            for class_name, prob in zip(self.class_names, probabilities)
        }

        # Confidence Policy / Low-Confidence Abstention Architecture
        min_threshold = settings.min_confidence_threshold
        is_confident = confidence >= min_threshold
        confidence_status = "possible_pattern" if is_confident else "insufficient_confidence"

        return {
            "success": True,
            "predicted_concern": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": probabilities_dict,
            "model_version": settings.model_version,
            "confidence_status": confidence_status,
            "is_confident": is_confident,
            "threshold_used": min_threshold,
        }


_predictor = None


def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = EfficientNetSkinConcernPredictor()
    return _predictor


def predict_skin_concern(image_bytes: bytes):
    predictor = get_predictor()
    return predictor.predict(image_bytes)