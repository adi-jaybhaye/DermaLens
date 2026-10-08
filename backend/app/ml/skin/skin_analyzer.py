import cv2
import numpy as np

from app.ml.model.efficientnet_predictor import predict_skin_concern


def analyze_skin_regions(
    image_bytes: bytes,
    regions: dict,
):
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

    image_height, image_width = image.shape[:2]

    results = {}

    for region_name, region in regions.items():

        x = max(0, int(region["x"]))
        y = max(0, int(region["y"]))
        width = int(region["width"])
        height = int(region["height"])

        x2 = min(image_width, x + width)
        y2 = min(image_height, y + height)

        if x >= x2 or y >= y2:
            results[region_name] = {
                "valid": False,
                "reason": "Invalid region",
            }
            continue

        roi = image[y:y2, x:x2]

        if roi.size == 0:
            results[region_name] = {
                "valid": False,
                "reason": "Empty region",
            }
            continue

        # ----------------------------------------------------
        # Supporting image/texture analysis
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY,
        )

        mean_brightness = float(np.mean(gray))
        brightness_std = float(np.std(gray))

        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F,
        )

        texture_variance = float(
            laplacian.var()
        )

        # ----------------------------------------------------
        # EfficientNet-B0 prediction
        # ----------------------------------------------------

        prediction_success = False
        prediction = None

        try:
            success, encoded_image = cv2.imencode(
                ".jpg",
                roi,
            )

            if success:
                region_bytes = encoded_image.tobytes()

                prediction = predict_skin_concern(
                    region_bytes
                )

                prediction_success = prediction.get(
                    "success",
                    False,
                )

        except Exception as exc:
            prediction = {
                "success": False,
                "reason": str(exc),
            }

        # ----------------------------------------------------
        # Region result
        # ----------------------------------------------------

        results[region_name] = {
            "valid": True,

            "width": int(roi.shape[1]),
            "height": int(roi.shape[0]),

            "mean_brightness": round(
                mean_brightness,
                2,
            ),

            "brightness_std": round(
                brightness_std,
                2,
            ),

            "texture_variance": round(
                texture_variance,
                2,
            ),

            "ml_prediction": (
                prediction
                if prediction_success
                else {
                    "success": False,
                    "reason": (
                        prediction.get(
                            "reason",
                            "Prediction failed",
                        )
                        if prediction
                        else "Prediction failed"
                    ),
                }
            ),
        }

    return {
        "success": True,
        "regions": results,
    }