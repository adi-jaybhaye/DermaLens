import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = BASE_DIR / "models"
BLAZE_FACE_PATH = str(MODELS_DIR / "blaze_face_short_range.tflite")
FACE_LANDMARKER_PATH = str(MODELS_DIR / "face_landmarker.task")


def detect_face(image_bytes: bytes):
    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        return None

    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image,
    )

    options = mp.tasks.vision.FaceDetectorOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=BLAZE_FACE_PATH
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        min_detection_confidence=0.5,
    )

    with mp.tasks.vision.FaceDetector.create_from_options(
        options
    ) as detector:

        result = detector.detect(mp_image)

    if not result.detections:
        return {
            "success": False,
            "reason": "No face detected",
            "face_count": 0,
        }

    if len(result.detections) != 1:
        return {
            "success": False,
            "reason": "Exactly one face is required",
            "face_count": len(result.detections),
        }

    detection = result.detections[0]
    bbox = detection.bounding_box

    confidence = None

    if detection.categories:
        confidence = detection.categories[0].score

    return {
        "success": True,
        "face_count": 1,
        "bounding_box": {
            "x": bbox.origin_x,
            "y": bbox.origin_y,
            "width": bbox.width,
            "height": bbox.height,
        },
        "confidence": confidence,
    }


def extract_landmarks(image_bytes: bytes):
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
            "success": False,
            "reason": "Invalid image data",
        }

    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image,
    )

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=FACE_LANDMARKER_PATH
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with mp.tasks.vision.FaceLandmarker.create_from_options(
        options
    ) as landmarker:

        result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        return {
            "success": False,
            "reason": "No facial landmarks detected",
        }

    landmarks = result.face_landmarks[0]

    height, width = image.shape[:2]

    points = []

    for index, landmark in enumerate(landmarks):
        points.append(
            {
                "index": index,
                "x": round(landmark.x * width, 2),
                "y": round(landmark.y * height, 2),
                "z": round(landmark.z, 5),
            }
        )

    return {
        "success": True,
        "landmark_count": len(points),
        "landmarks": points,
    }

def extract_face_regions(image_bytes: bytes):
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
            "success": False,
            "reason": "Invalid image data",
        }

    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image,
    )

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=FACE_LANDMARKER_PATH
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with mp.tasks.vision.FaceLandmarker.create_from_options(
        options
    ) as landmarker:

        result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        return {
            "success": False,
            "reason": "No facial landmarks detected",
        }

    landmarks = result.face_landmarks[0]

    height, width = image.shape[:2]

    points = np.array(
        [
            [
                int(landmark.x * width),
                int(landmark.y * height),
            ]
            for landmark in landmarks
        ],
        dtype=np.int32,
    )

    # MediaPipe face-oval landmarks.
    face_oval_indices = [
        10, 338, 297, 332, 284, 251, 389, 356,
        454, 323, 361, 288, 397, 365, 379, 378,
        400, 377, 152, 148, 176, 149, 150, 136,
        172, 58, 132, 93, 234, 127, 162, 21,
        54, 103, 67, 109
    ]

    face_oval = points[face_oval_indices]

    # Approximate facial region anchors.
    left_face_x = int(np.min(face_oval[:, 0]))
    right_face_x = int(np.max(face_oval[:, 0]))
    top_face_y = int(np.min(face_oval[:, 1]))
    bottom_face_y = int(np.max(face_oval[:, 1]))

    face_width = right_face_x - left_face_x
    face_height = bottom_face_y - top_face_y

    center_x = (left_face_x + right_face_x) // 2

    # Region boxes are derived from the detected face geometry.
    regions = {
        "forehead": (
            left_face_x + int(face_width * 0.22),
            top_face_y + int(face_height * 0.08),
            right_face_x - int(face_width * 0.22),
            top_face_y + int(face_height * 0.30),
        ),

        "left_cheek": (
            left_face_x + int(face_width * 0.08),
            top_face_y + int(face_height * 0.38),
            center_x - int(face_width * 0.04),
            top_face_y + int(face_height * 0.68),
        ),

        "right_cheek": (
            center_x + int(face_width * 0.04),
            top_face_y + int(face_height * 0.38),
            right_face_x - int(face_width * 0.08),
            top_face_y + int(face_height * 0.68),
        ),

        "nose": (
            center_x - int(face_width * 0.13),
            top_face_y + int(face_height * 0.30),
            center_x + int(face_width * 0.13),
            top_face_y + int(face_height * 0.62),
        ),

        "chin": (
            left_face_x + int(face_width * 0.25),
            top_face_y + int(face_height * 0.68),
            right_face_x - int(face_width * 0.25),
            bottom_face_y - int(face_height * 0.05),
        ),
    }

    region_results = {}

    for region_name, (x1, y1, x2, y2) in regions.items():

        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        region_results[region_name] = {
            "x": x1,
            "y": y1,
            "width": max(0, x2 - x1),
            "height": max(0, y2 - y1),
        }

    return {
        "success": True,
        "image_width": width,
        "image_height": height,
        "regions": region_results,
    }