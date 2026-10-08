import json
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = BASE_DIR / "training" / "outputs"
MODEL_DIR = BASE_DIR / "training" / "models"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 1e-4
VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ============================================================
# Reproducibility
# ============================================================

torch.manual_seed(RANDOM_SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)


# ============================================================
# Image transformations
# ============================================================

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15,
        saturation=0.10,
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


validation_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


# ============================================================
# Dataset
# ============================================================

def create_datasets():
    full_dataset = datasets.ImageFolder(
        root=DATASET_DIR,
        transform=train_transform,
    )

    total_size = len(full_dataset)
    validation_size = int(total_size * VALIDATION_SPLIT)
    training_size = total_size - validation_size

    generator = torch.Generator().manual_seed(RANDOM_SEED)

    train_dataset, validation_dataset = random_split(
        full_dataset,
        [training_size, validation_size],
        generator=generator,
    )

    # Validation must not use training augmentation.
    validation_base = datasets.ImageFolder(
        root=DATASET_DIR,
        transform=validation_transform,
    )

    validation_dataset.dataset = validation_base

    return train_dataset, validation_dataset, full_dataset.classes


# ============================================================
# Model
# ============================================================

def create_model(num_classes):
    weights = models.EfficientNet_B0_Weights.DEFAULT

    model = models.efficientnet_b0(weights=weights)

    # Replace the final classifier layer.
    input_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        input_features,
        num_classes,
    )

    return model


# ============================================================
# Training
# ============================================================

def train_one_epoch(model, loader, criterion, optimizer):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

        predictions = outputs.argmax(dim=1)

        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total

    return epoch_loss, epoch_accuracy


# ============================================================
# Validation
# ============================================================

def validate(model, loader, criterion):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    validation_loss = running_loss / total
    validation_accuracy = correct / total

    return validation_loss, validation_accuracy


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("EfficientNet-B0 Skin Concern Training")
    print("=" * 60)

    print(f"Dataset: {DATASET_DIR}")
    print(f"Device: {DEVICE}")

    train_dataset, validation_dataset, class_names = create_datasets()

    print(f"Classes: {class_names}")
    print(f"Training images: {len(train_dataset)}")
    print(f"Validation images: {len(validation_dataset)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    model = create_model(len(class_names))
    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    best_validation_accuracy = 0.0

    history = []

    for epoch in range(EPOCHS):
        print()
        print(
            f"Epoch {epoch + 1}/{EPOCHS}"
        )

        train_loss, train_accuracy = train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
        )

        validation_loss, validation_accuracy = validate(
            model,
            validation_loader,
            criterion,
        )

        print(
            f"Train Loss: {train_loss:.4f} | "
            f"Train Accuracy: {train_accuracy:.4f}"
        )

        print(
            f"Validation Loss: {validation_loss:.4f} | "
            f"Validation Accuracy: {validation_accuracy:.4f}"
        )

        history.append({
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "validation_loss": validation_loss,
            "validation_accuracy": validation_accuracy,
        })

        if validation_accuracy > best_validation_accuracy:
            best_validation_accuracy = validation_accuracy

            model_path = MODEL_DIR / "efficientnet_b0_skin_concerns.pth"

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": class_names,
                    "image_size": IMAGE_SIZE,
                },
                model_path,
            )

            print(f"Best model saved: {model_path}")

    history_path = OUTPUT_DIR / "training_history.json"

    with open(history_path, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)

    classes_path = OUTPUT_DIR / "class_names.json"

    with open(classes_path, "w", encoding="utf-8") as file:
        json.dump(class_names, file, indent=4)

    print()
    print("=" * 60)
    print("Training completed.")
    print(f"Best validation accuracy: {best_validation_accuracy:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()