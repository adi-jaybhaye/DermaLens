import cv2
import numpy as np


def check_image_quality(image_bytes: bytes) -> dict:
    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        return {
            "valid": False,
            "reason": "Invalid image",
        }

    height, width = image.shape[:2]

    # Minimum resolution
    if width < 300 or height < 300:
        return {
            "valid": False,
            "reason": "Image resolution is too low",
        }

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    # Blur detection using Laplacian variance
    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F,
    ).var()

    # Overall brightness
    brightness = float(np.mean(gray))

    issues = []

    if blur_score < 50:
        issues.append("Image is too blurry")

    if brightness < 40:
        issues.append("Image is too dark")

    if brightness > 220:
        issues.append("Image is overexposed")

    return {
        "valid": len(issues) == 0,
        "width": width,
        "height": height,
        "blur_score": round(float(blur_score), 2),
        "brightness": round(brightness, 2),
        "issues": issues,
    }