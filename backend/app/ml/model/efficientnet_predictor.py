from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io


BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BASE_DIR
    / "training"
    / "models"
    / "efficientnet_b0_skin_concerns.pth"
)

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


class EfficientNetSkinConcernPredictor:

    def __init__(self):
        checkpoint = torch.load(
            MODEL_PATH,
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

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model.to(DEVICE)
        self.model.eval()

    def predict(self, image_bytes: bytes):

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        tensor = TRANSFORM(image)

        tensor = tensor.unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            outputs = self.model(tensor)

            probabilities = torch.softmax(
                outputs,
                dim=1,
            )[0]

            predicted_index = torch.argmax(
                probabilities
            ).item()

        predicted_class = self.class_names[
            predicted_index
        ]

        confidence = float(
            probabilities[predicted_index].item()
        )

        probabilities_dict = {
            class_name: round(
                float(probability.item()),
                4,
            )
            for class_name, probability in zip(
                self.class_names,
                probabilities,
            )
        }

        return {
            "success": True,
            "predicted_concern": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": probabilities_dict,
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