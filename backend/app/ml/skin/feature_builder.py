def build_feature_vector(skin_analysis: dict) -> dict:
    if not skin_analysis.get("success"):
        return {
            "success": False,
            "reason": "Skin analysis failed",
        }

    regions = skin_analysis.get("regions", {})

    region_order = [
        "forehead",
        "left_cheek",
        "right_cheek",
        "nose",
        "chin",
    ]

    feature_vector = []
    feature_names = []

    for region_name in region_order:
        region = regions.get(region_name)

        if not region or not region.get("valid"):
            return {
                "success": False,
                "reason": f"Invalid or missing region: {region_name}",
            }

        features = [
            ("mean_brightness", region["mean_brightness"]),
            ("brightness_std", region["brightness_std"]),
            ("texture_variance", region["texture_variance"]),
        ]

        for feature_name, value in features:
            feature_names.append(
                f"{region_name}_{feature_name}"
            )
            feature_vector.append(float(value))

    return {
        "success": True,
        "feature_count": len(feature_vector),
        "feature_names": feature_names,
        "feature_vector": feature_vector,
    }