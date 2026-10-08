"""
Grad-CAM (Gradient-weighted Class Activation Mapping) for EfficientNet-B0.

Generates visual explanations showing which image regions contributed
most to the model's prediction. Returns base64-encoded heatmap and
overlay images suitable for API responses.

IMPORTANT: Grad-CAM is an explanation aid. It is NOT proof of medical
causality, disease, or biological mechanism.
"""

import base64
import io

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from app.ml.model.efficientnet_predictor import (
    get_predictor,
    TRANSFORM,
    DEVICE,
)


def generate_gradcam(
    image_bytes: bytes,
    target_class: int = None,
):
    """Generate a Grad-CAM heatmap for an image.

    Args:
        image_bytes: Raw image bytes (JPEG, PNG, or WebP).
        target_class: Class index to explain. If None, the predicted
                      (argmax) class is used.

    Returns:
        dict with prediction info and base64-encoded visualisations.
    """
    predictor = get_predictor()
    model = predictor.model

    # Load and prepare image
    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    original_np = np.array(image)

    input_tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

    # Register hooks on the last convolutional block
    activations = []
    gradients = []

    target_layer = model.features[-1]

    def forward_hook(module, inputs, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    forward_handle = target_layer.register_forward_hook(
        forward_hook
    )
    backward_handle = target_layer.register_full_backward_hook(
        backward_hook
    )

    try:
        # Forward pass
        model.zero_grad()
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)[0]

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        # Backward pass for the target class
        score = output[0, target_class]
        score.backward()
    finally:
        # Always remove hooks to prevent accumulation
        forward_handle.remove()
        backward_handle.remove()

    # Compute Grad-CAM
    activation = activations[0]
    gradient = gradients[0]

    weights = gradient.mean(dim=(2, 3), keepdim=True)
    cam = (weights * activation).sum(dim=1)
    cam = F.relu(cam)
    cam = cam[0].detach().cpu().numpy()

    if cam.max() > 0:
        cam = cam / cam.max()

    # Resize CAM to original image dimensions
    cam_resized = cv2.resize(
        cam,
        (image.width, image.height),
    )

    # Create coloured heatmap (JET colourmap)
    heatmap_coloured = cv2.applyColorMap(
        np.uint8(255 * cam_resized),
        cv2.COLORMAP_JET,
    )
    heatmap_coloured = cv2.cvtColor(
        heatmap_coloured,
        cv2.COLOR_BGR2RGB,
    )

    # Create overlay (40 % heatmap + 60 % original)
    overlay = (
        np.float32(heatmap_coloured) * 0.4
        + np.float32(original_np) * 0.6
    )
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    # Encode overlay as base64 PNG
    overlay_pil = Image.fromarray(overlay)
    buf_overlay = io.BytesIO()
    overlay_pil.save(buf_overlay, format="PNG")
    overlay_base64 = base64.b64encode(
        buf_overlay.getvalue()
    ).decode("utf-8")

    # Encode heatmap as base64 PNG
    heatmap_pil = Image.fromarray(heatmap_coloured)
    buf_heatmap = io.BytesIO()
    heatmap_pil.save(buf_heatmap, format="PNG")
    heatmap_base64 = base64.b64encode(
        buf_heatmap.getvalue()
    ).decode("utf-8")

    # Build class probabilities dict
    predicted_class = predictor.class_names[target_class]
    confidence = float(probabilities[target_class].item())

    all_probabilities = {
        name: round(float(prob.item()), 4)
        for name, prob in zip(
            predictor.class_names,
            probabilities,
        )
    }

    return {
        "success": True,
        "predicted_concern": predicted_class,
        "confidence": round(confidence, 4),
        "probabilities": all_probabilities,
        "heatmap_base64": heatmap_base64,
        "overlay_base64": overlay_base64,
    }