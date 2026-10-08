import numpy as np


# MediaPipe Face Landmarker landmark indices
FOREHEAD = [10, 67, 109, 103, 104, 105, 66, 107]

LEFT_CHEEK = [116, 117, 118, 119, 120, 121, 47, 207, 206, 205]

RIGHT_CHEEK = [345, 346, 347, 348, 349, 350, 277, 427, 426, 425]

NOSE = [1, 2, 4, 5, 6, 19, 94, 168]

CHIN = [152, 148, 176, 149, 150, 136, 172]


FACIAL_REGIONS = {
    "forehead": FOREHEAD,
    "left_cheek": LEFT_CHEEK,
    "right_cheek": RIGHT_CHEEK,
    "nose": NOSE,
    "chin": CHIN,
}


def get_region_points(landmarks, region_name):
    indices = FACIAL_REGIONS.get(region_name)

    if indices is None:
        raise ValueError(f"Unknown facial region: {region_name}")

    points = []

    for index in indices:
        landmark = landmarks[index]

        points.append(
            [
                landmark["x"],
                landmark["y"],
            ]
        )

    return np.array(points, dtype=np.float32)


def get_all_regions(landmarks):
    return {
        region_name: get_region_points(
            landmarks,
            region_name,
        ).tolist()
        for region_name in FACIAL_REGIONS
    }