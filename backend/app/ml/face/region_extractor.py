import cv2
import numpy as np


def extract_region_crops(image_bytes: bytes, landmarks: list):
    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        return {}


    regions = {
        "forehead": [10, 67, 109, 103, 104, 105, 66, 107],
        "left_cheek": [116, 117, 118, 119, 120, 121, 47, 207, 206, 205],
        "right_cheek": [345, 346, 347, 348, 349, 350, 277, 427, 426, 425],
        "nose": [1, 2, 4, 5, 6, 19, 94, 168],
        "chin": [152, 148, 176, 149, 150, 136, 172],
    }

    height, width = image.shape[:2]

    crops = {}

    for region_name, indices in regions.items():

        points = []

        for index in indices:
            x = int(landmarks[index]["x"])
            y = int(landmarks[index]["y"])

            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))

            points.append([x, y])

        points = np.array(points, dtype=np.int32)

        x, y, w, h = cv2.boundingRect(points)

        # Small padding around the region
        padding = 10

        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)

        crop = image[y1:y2, x1:x2]

        crops[region_name] = crop

    return crops