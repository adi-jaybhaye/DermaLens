import json
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from sklearn.metrics import classification_report, confusion_matrix


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
MODEL_PATH = BASE_DIR / "training" / "models" / "efficientnet_b0_skin_concerns.pth"
OUTPUT_DIR = BASE_DIR / "training" / "outputs"

IMAGE_SIZE = 224
BATCH_SIZE = 16
RANDOM_SEED = 42

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def main():
    print("=" * 60)
    print("EfficientNet-B0 Evaluation")
    print("=" * 60)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True,
    )

    class_names = checkpoint["class_names"]

    dataset = datasets.ImageFolder(
        root=DATASET_DIR,
        transform=transform,
    )

    validation_size = int(len(dataset) * 0.2)
    training_size = len(dataset) - validation_size

    generator = torch.Generator().manual_seed(RANDOM_SEED)

    _, validation_dataset = random_split(
        dataset,
        [training_size, validation_size],
        generator=generator,
    )

    loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    model = models.efficientnet_b0(weights=None)

    input_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        input_features,
        len(class_names),
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(DEVICE)
    model.eval()

    all_labels = []
    all_predictions = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(DEVICE)

            outputs = model(images)
            predictions = outputs.argmax(dim=1)

            all_labels.extend(labels.tolist())
            all_predictions.extend(predictions.cpu().tolist())

    print()
    print("Classification Report")
    print("=" * 60)

    report = classification_report(
        all_labels,
        all_predictions,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )

    print(report)

    print("Confusion Matrix")
    print("=" * 60)

    matrix = confusion_matrix(
        all_labels,
        all_predictions,
    )

    print(matrix)

    report_path = OUTPUT_DIR / "classification_report.txt"

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)
        file.write("\n\nConfusion Matrix\n")
        file.write(str(matrix))

    print()
    print(f"Evaluation saved to: {report_path}")


if __name__ == "__main__":
    main()