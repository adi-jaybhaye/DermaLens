from app.ml.model.preprocessor import prepare_features


def predict_skin_condition(feature_vector):
    features = prepare_features(feature_vector)

    return {
        "success": False,
        "status": "MODEL_NOT_TRAINED",
        "feature_shape": list(features.shape),
        "message": "Skin-condition model is not trained yet.",
    }