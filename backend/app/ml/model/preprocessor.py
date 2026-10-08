import numpy as np


def prepare_features(feature_vector):
    if not feature_vector:
        raise ValueError("Feature vector is empty")

    features = np.asarray(
        feature_vector,
        dtype=np.float32,
    )

    if features.ndim != 1:
        raise ValueError(
            "Feature vector must be one-dimensional"
        )

    if len(features) != 15:
        raise ValueError(
            f"Expected 15 features, got {len(features)}"
        )

    return features.reshape(1, -1)