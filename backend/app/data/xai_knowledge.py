"""
Curated two-level Explainable AI (XAI) knowledge base for DermaLens.

Strictly grounded in the peer-reviewed research and authoritative clinical reference
documents stored in backend/data/research/.

Level 1: Very easy, everyday conversational language (short, accessible sentences).
Level 2: Substantially detailed "Learn More" scientific explanation (explaining
         all biological and biophysical concepts immediately in plain words).

Strict separation between:
- MODEL REASONING (how the visual neural network evaluated image features)
- SCIENTIFIC BACKGROUND (what dermatological science knows about the skin feature)
"""

from typing import Any, Optional
from app.data.evidence_sources import EVIDENCE_SOURCES, get_sources_for_concern


REGION_HUMAN_NAMES = {
    "forehead": "forehead",
    "left_cheek": "left cheek",
    "right_cheek": "right cheek",
    "nose": "nose and midface",
    "chin": "chin and jawline",
}


XAI_CONCERNS_KNOWLEDGE: dict[str, dict[str, Any]] = {
    # ------------------------------------------------------------------
    # 1. Redness
    # ------------------------------------------------------------------
    "Redness": {
        "concept": "Redness",
        "display_name": "Redness (Erythema)",
        "level1": {
            "what_we_noticed": (
                "The photo shows areas with a pink or reddish tone that stand out "
                "from the surrounding skin."
            ),
            "where_we_noticed_it_template": "In the {region_name} area.",
            "why_ai_identified_it": (
                "The AI compared this photo to thousands of skin images it studied during "
                "training. It noticed localized reddish tones and subtle contrast differences "
                "that match visual redness patterns."
            ),
            "why_it_can_occur": (
                "Tiny blood vessels right under the surface of the skin can temporarily "
                "widen, bringing more blood to the area. This can happen after warm temperatures, "
                "sun exposure, mild irritation, or certain skin conditions. A photo alone "
                "cannot tell us the specific reason for one individual."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted colors on the image show which visual pixels influenced the "
                "AI's prediction most strongly. This is an explanation aid to show where the "
                "computer looked. It does not show the biological cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "In dermatological science, visible redness is termed erythema. It occurs when "
                "microscopic blood vessels (capillaries) in the upper layer of the dermis expand—a "
                "process called vasodilation. Expanding vessels allow increased blood flow close to "
                "the skin surface, causing the skin to look pink or red. Vasodilation is a natural "
                "physiological reaction that can be triggered by external warmth, sun exposure, "
                "emotional flushing, or a temporary disruption of the protective outer skin barrier. "
                "It can also accompany persistent inflammatory skin conditions such as rosacea or "
                "seborrheic dermatitis. However, because many different factors produce the exact same "
                "red appearance on a camera sensor, an image cannot determine the physiological or "
                "medical mechanism in any individual."
            ),
            "contributing_factors": [
                "Sunlight and ultraviolet (UV) exposure",
                "Temperature changes, heat, or cold wind",
                "Temporary skin barrier irritation or sensitive skin",
                "Topical skincare ingredients or gentle friction",
                "Flushing responses or underlying conditions like rosacea",
            ],
            "limitations": (
                "Scientific research emphasizes that visible redness is an etiologically non-specific sign. "
                "That means different skin processes look identical in a photograph. A standard 2D camera "
                "cannot measure capillary blood flow, assess vascular responsiveness, or distinguish "
                "transient irritation from an underlying dermatological condition."
            ),
            "source_ids": ["SRC-12", "SRC-01", "SRC-02", "SRC-27"],
            "safety_guidance": (
                "If facial redness persists for more than two weeks, spreads, feels warm, burns, or is "
                "accompanied by swelling or discomfort, schedule an in-person consultation with a "
                "board-certified dermatologist for a clinical evaluation."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 2. Dark Spots
    # ------------------------------------------------------------------
    "dark spots": {
        "concept": "dark spots",
        "display_name": "Dark Spots (Hyperpigmentation)",
        "level1": {
            "what_we_noticed": (
                "The photo contains small, localized patches that appear darker than the nearby skin."
            ),
            "where_we_noticed_it_template": "In the {region_name} area.",
            "why_ai_identified_it": (
                "The AI compared the colors and borders in this image with patterns it learned "
                "from training photos. It spotted small, defined areas of deeper contrast and darker color."
            ),
            "why_it_can_occur": (
                "Skin makes a natural pigment called melanin to protect itself. When pigment-producing "
                "cells create extra color in one spot—often after a blemish, a scratch, or sun exposure—a "
                "dark mark can linger. A photo alone cannot tell us the exact personal reason."
            ),
        },
        "heatmap": {
            "explanation": (
                "The colored highlights show which specific patches and edges guided the AI's "
                "visual assessment. This is an explanation aid to show the model's focus, not a "
                "medical test or proof of skin disease."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "Dark spots are localized areas of hyperpigmentation. Skin color is created by a dark "
                "biological pigment called melanin, produced by specialized cells called melanocytes "
                "located in the basal layer of the epidermis. When skin undergoes inflammation (such "
                "as after acne, an insect bite, or a cut), inflammatory messengers stimulate nearby "
                "melanocytes to produce extra melanin. This melanin gets deposited into surrounding "
                "skin cells, creating a spot known as post-inflammatory hyperpigmentation (PIH). "
                "Cumulative exposure to ultraviolet (UV) sunlight also stimulates melanocytes, forming "
                "sun spots (solar lentigines). While the pigment is harmless in most instances, a "
                "standard photograph cannot determine the exact microscopic depth of the pigment "
                "or confirm its biological origin."
            ),
            "contributing_factors": [
                "Prior skin inflammation or healing blemishes (post-inflammatory hyperpigmentation)",
                "Cumulative exposure to sunlight and ultraviolet (UV) radiation",
                "Natural hormonal fluctuations (such as pregnancy or oral contraceptives)",
                "Physical friction, scratching, or picking at healing skin",
                "Genetic tendency to produce higher amounts of protective melanin",
            ],
            "limitations": (
                "A 2D digital image cannot evaluate the microscopic depth of pigment (whether it sits in "
                "the superficial epidermis or deeper dermis), nor can it replace a dermatoscope. Any dark "
                "spot that is changing in size, shape, or color requires a clinical medical examination."
            ),
            "source_ids": ["SRC-11", "SRC-03", "SRC-26B"],
            "safety_guidance": (
                "Most superficial dark spots are benign. However, if any spot has uneven borders, "
                "shows multiple colors, changes in size, bleeds, or itches, consult a dermatologist "
                "promptly according to the ABCDE skin safety guidelines."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 3. Inflammatory Acne
    # ------------------------------------------------------------------
    "inflammatory acne": {
        "concept": "inflammatory acne",
        "display_name": "Inflammatory Blemishes",
        "level1": {
            "what_we_noticed": (
                "The photo shows small raised bumps with visible redness or swelling around them."
            ),
            "where_we_noticed_it_template": "Across the {region_name} area.",
            "why_ai_identified_it": (
                "The AI recognized elevated surface contours paired with localized reddish color shifts "
                "that match training examples of inflamed blemishes."
            ),
            "why_it_can_occur": (
                "When a pore gets clogged with natural skin oil and dead skin cells, local bacteria can "
                "trigger a temporary immune response. This leads to mild swelling and redness. A photo "
                "alone cannot identify an individual's internal hormonal or dietary factors."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted regions indicate which raised contours and red pixels contributed "
                "most to the AI's pattern prediction. This is an explanation aid to show where the "
                "system focused. It does not show the biological cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "Inflammatory acne lesions occur within the pilosebaceous unit—the anatomical structure "
                "combining a hair follicle and its connected sebaceous (oil) gland. Under the influence "
                "of hormones, sebaceous glands can produce extra oil (sebum), while dead skin cells "
                "accumulate and block the follicle opening. Naturally occurring skin bacteria "
                "(Cutibacterium acnes) multiply inside the trapped sebum, causing the immune system to "
                "send white blood cells and inflammatory signals. This inflammatory response produces "
                "tender red bumps (papules) or bumps containing visible fluid (pustules). Research "
                "shows that squeezing or picking blemishes pushes inflammation deeper into the dermis, "
                "increasing tissue damage and the likelihood of lasting dark marks or scars."
            ),
            "contributing_factors": [
                "Increased sebum (skin oil) secretion",
                "Accumulation of shed skin cells inside the follicle opening",
                "Activity of natural Cutibacterium acnes bacteria within clogged pores",
                "Hormonal changes (including puberty, monthly cycles, or stress hormones)",
                "Mechanical friction, touching the face, or heavy comedogenic skincare",
            ],
            "limitations": (
                "Visual image analysis cannot measure bacterial colonization, assess lesion tenderness, "
                "measure internal follicular swelling depth, or establish a medical treatment plan. "
                "A visual pattern does not equal an official dermatological diagnosis."
            ),
            "source_ids": ["SRC-08", "SRC-10", "SRC-04"],
            "safety_guidance": (
                "Avoid squeezing or popping blemishes, which can spread bacteria and cause scarring. "
                "If blemishes are deep, painful, widespread, or leave lingering marks, consult a "
                "board-certified dermatologist for safe, evidence-based management."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 4. Non-inflammatory Acne — Blackheads (Open Comedones)
    # ------------------------------------------------------------------
    "non inflammatory acne black heads": {
        "concept": "non inflammatory acne black heads",
        "display_name": "Blackheads (Open Comedones)",
        "level1": {
            "what_we_noticed": (
                "The photo shows tiny, dark specks resting at the surface of skin pores."
            ),
            "where_we_noticed_it_template": "Across the {region_name} area.",
            "why_ai_identified_it": (
                "The AI spotted small, dark circular dots contrasting against the surrounding "
                "skin, matching patterns of open pore plugs from its training images."
            ),
            "why_it_can_occur": (
                "When a pore gets plugged with skin oil and shed cells but stays open to the air, "
                "contact with oxygen turns the mixture dark. This is a natural reaction, not trapped "
                "dirt. A photo cannot determine your exact oil-production levels."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted area marks the small surface dots that influenced the AI model. "
                "This visual guide shows where the AI looked on the image. It does not show the "
                "biological cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "In medical terminology, a blackhead is called an open comedo. It develops when a hair "
                "follicle opening becomes plugged with a mixture of sebum (natural skin oil) and shed "
                "corneocytes (dead skin cells). Unlike a pimple, there is no active bacterial infection "
                "or significant redness. Because the pore's surface opening remains open, the trapped "
                "mixture is directly exposed to atmospheric oxygen. The oxygen reacts chemically with "
                "melanin and lipids in the plug (a process called oxidation), turning the top of the "
                "plug dark brown or black. Contrary to popular belief, blackheads are not caused by dirt "
                "and cannot simply be scrubbed away with harsh physical pressure."
            ),
            "contributing_factors": [
                "Natural sebum (oil) secretion filling the follicular canal",
                "Gradual accumulation of shed skin cells that adhere together",
                "Exposure of the plugged opening to air, causing oxidation",
                "Comedogenic cosmetic ingredients that encourage pore clogging",
                "Hormonal signals that stimulate sebaceous gland activity",
            ],
            "limitations": (
                "Camera images often struggle to distinguish true open comedones from normal, healthy "
                "sebaceous filaments (natural channels that guide oil to the surface). A photograph "
                "cannot test the physical contents of a pore or measure sebum viscosity."
            ),
            "source_ids": ["SRC-15", "SRC-08", "SRC-04"],
            "safety_guidance": (
                "Gentle cleansing and mild chemical exfoliants (such as salicylic acid) are safer than "
                "aggressive metal extraction tools or harsh squeezing, which can tear delicate pore "
                "walls and trigger inflammation."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 5. Non-inflammatory Acne — Whiteheads (Closed Comedones)
    # ------------------------------------------------------------------
    "non inflammatory acne white heads": {
        "concept": "non inflammatory acne white heads",
        "display_name": "Whiteheads (Closed Comedones)",
        "level1": {
            "what_we_noticed": (
                "The photo shows small, pale, or skin-colored bumps that are smooth and not visibly inflamed."
            ),
            "where_we_noticed_it_template": "In the {region_name} area.",
            "why_ai_identified_it": (
                "The AI detected subtle, small rounded elevations that change the skin's surface "
                "smoothness without showing the strong redness of inflamed spots."
            ),
            "why_it_can_occur": (
                "When a pore's opening is very narrow or covered by a thin layer of cells, trapped oil "
                "and dead skin stay shielded from the air, creating a tiny pale bump. A photo cannot "
                "tell us what caused the buildup in a specific person."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted overlay shows the small textural bumps that the AI detected. "
                "This visual guide illustrates the model's focus. It does not show the biological "
                "cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "A whitehead is clinically known as a closed comedo. Similar to a blackhead, it forms "
                "when excess sebum and shed skin cells build up inside a hair follicle. However, in a "
                "closed comedo, the pore opening is extremely narrow or capped by a microscopic layer of "
                "keratinocytes. Because the trapped contents are shielded from the open air, oxidation "
                "does not take place. The plug retains its natural pale, whitish, or skin-toned appearance, "
                "presenting as a tiny, non-inflamed bump slightly elevating the skin surface. Because closed "
                "comedones lack an opening, forcing them with fingernails or sharp objects can rupture the "
                "follicle wall into surrounding tissue, causing painful inflammation and scarring."
            ),
            "contributing_factors": [
                "Trapping of natural sebum beneath a narrow follicular opening",
                "Sluggish turnover of dead skin cells at the pore surface",
                "Use of heavy, occlusive creams or comedogenic cosmetics",
                "Hormonal factors influencing sebum production and cell shedding",
                "Gentle skin friction from masks, hats, or pillowcases",
            ],
            "limitations": (
                "On standard 2D photos, closed comedones can easily be confused with other benign skin "
                "features such as milia (tiny keratin cysts) or sebaceous hyperplasia. Lighting angle "
                "heavily influences their visibility in camera crops."
            ),
            "source_ids": ["SRC-15", "SRC-08", "SRC-10"],
            "safety_guidance": (
                "Never pick or puncture closed comedones at home, as puncture without sterile technique "
                "creates high risk of infection and scarring. A dermatologist can provide professional "
                "topical therapies (such as prescription retinoids) or clinical extractions."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 6. Pigmentation
    # ------------------------------------------------------------------
    "pigmentation": {
        "concept": "pigmentation",
        "display_name": "Uneven Pigmentation",
        "level1": {
            "what_we_noticed": (
                "The photo shows broader areas of uneven skin tone or brownish shading across the area."
            ),
            "where_we_noticed_it_template": "Across the {region_name} area.",
            "why_ai_identified_it": (
                "The AI identified gentle variations in shading and light absorption across the skin "
                "surface, matching training examples of diffuse pigment patterns."
            ),
            "why_it_can_occur": (
                "Specialized skin cells can produce extra natural color when triggered by sunlight, "
                "hormones, or skin stress. These variations often spread across broader patches rather "
                "than tiny single dots. A photo cannot tell us your personal biological trigger."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted regions show which areas of color variation and contrast guided "
                "the AI's assessment. This is an explanation aid showing image focus. It does not "
                "show the biological cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "Uneven facial pigmentation refers to broader distributions of melanin across the "
                "skin surface, frequently presenting in patterns such as melasma. Melanocytes (pigment-"
                "producing cells in the epidermis) synthesize melanin inside cellular structures called "
                "melanosomes, then distribute this pigment to neighboring keratinocytes. Ultraviolet (UV) "
                "radiation from the sun is the strongest external trigger, activating melanogenesis to "
                "shield cell nuclei. Internal influences, especially estrogen and progesterone receptor "
                "signaling, also heighten melanocyte activity—which explains why diffuse pigmentation "
                "often becomes more noticeable during pregnancy or when using hormonal contraceptives. "
                "Scientific research demonstrates that deeper dermal factors, including chronic low-grade "
                "sun damage to elastic fibers, often accompany surface pigmentation patterns."
            ),
            "contributing_factors": [
                "Sun exposure (both ultraviolet rays and visible light stimulate melanin)",
                "Hormonal influences (pregnancy, oral contraceptives, hormonal therapy)",
                "Genetic predisposition and family history of pigmentary patterns",
                "Cumulative photoaging and environmental oxidative stress",
                "Heat exposure or prior cutaneous inflammation in the area",
            ],
            "limitations": (
                "Standard photographic imaging cannot assess whether pigment is deposited shallowly in "
                "the epidermis or deeper in dermal macrophages (which requires Wood's lamp or clinical "
                "dermatoscopy). Camera white balance and ambient room lighting can also alter perceived tone."
            ),
            "source_ids": ["SRC-09", "SRC-11", "SRC-03", "SRC-28"],
            "safety_guidance": (
                "Daily broad-spectrum sunscreen with high UVA/UVB protection is the most effective way "
                "to prevent pigmentation from deepening. If you notice rapidly spreading or changing "
                "patches, consult a dermatologist for personalized, safe management."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 7. Enlarged Pores
    # ------------------------------------------------------------------
    "pores": {
        "concept": "pores",
        "display_name": "Visible Pores",
        "level1": {
            "what_we_noticed": (
                "The photo shows small, visible circular openings or tiny surface texture depressions."
            ),
            "where_we_noticed_it_template": "Across the {region_name} area.",
            "why_ai_identified_it": (
                "The AI noticed repeated micro-shadows and subtle texture indentations on the skin surface "
                "that match pore patterns learned during training."
            ),
            "why_it_can_occur": (
                "Pores are completely normal openings that allow skin oil and sweat to reach the surface. "
                "They become more visible when skin produces more natural oil, when skin loses some of its "
                "firmness, or simply due to genetic skin texture. A photo alone cannot determine individual "
                "biological oil production or measure pore depth."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted colors show the micro-texture indentations and pore openings that the "
                "AI focused on. This is an explanation aid to show where the system looked. It does not "
                "show the biological cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "Facial pores are the visible surface openings of pilosebaceous units (carrying sebum "
                "from sebaceous glands) and sweat ducts. Pores are essential, healthy anatomical structures "
                "present on everyone's skin. Dermatological research shows that pore visibility is strongly "
                "correlated with higher casual sebum excretion—when more oil flows through the follicular "
                "duct, the opening appears more prominent. Additionally, as skin naturally ages or incurs "
                "sun damage, dermal collagen and elastin fibers surrounding the follicle gradually weaken, "
                "reducing the elastic tension that keeps pore walls taut. Pores do not possess muscles "
                "and therefore cannot physically 'open' or 'close' with cold water or steam, despite "
                "popular myths."
            ),
            "contributing_factors": [
                "Natural sebum (oil) excretion levels flowing through the follicle",
                "Genetic determination of hair follicle size and skin texture",
                "Age-related decrease in skin elasticity and supportive dermal collagen",
                "Cumulative sun exposure that degrades structural fibers around the pore",
                "Accumulation of unexfoliated dead cells at the pore rim",
            ],
            "limitations": (
                "Pores are normal structural features, not a pathology. Their apparent size in a camera "
                "crop is heavily influenced by camera resolution, lens distance, and oblique lighting angles "
                "that cast directional shadows across the skin."
            ),
            "source_ids": ["SRC-13", "SRC-04", "SRC-19", "SRC-27"],
            "safety_guidance": (
                "Pores cannot and should not be eliminated. Gentle cleansing, non-comedogenic hydration, "
                "and daily sun protection help preserve the skin's natural elastic framework around pores."
            ),
        },
    },

    # ------------------------------------------------------------------
    # 8. Wrinkles & Fine Lines
    # ------------------------------------------------------------------
    "wrinkles": {
        "concept": "wrinkles",
        "display_name": "Fine Lines & Creases",
        "level1": {
            "what_we_noticed": (
                "The photo shows fine surface lines or shallow creases along natural skin movement paths."
            ),
            "where_we_noticed_it_template": "Across the {region_name} area.",
            "why_ai_identified_it": (
                "The AI recognized subtle linear shadow patterns and skin contour grooves that match "
                "training examples of fine lines and creases."
            ),
            "why_it_can_occur": (
                "As skin naturally matures and moves with everyday smiles or frowns, it gradually loses "
                "some of its natural bounce and firmness. Sunlight over the years also speeds up this "
                "process. A photo cannot determine your exact skin collagen level."
            ),
        },
        "heatmap": {
            "explanation": (
                "The highlighted regions trace the linear surface shadows and contours that influenced "
                "the AI's assessment. This is an explanation aid to show where the system focused. It does "
                "not show the biological cause or confirm a medical diagnosis."
            ),
        },
        "learn_more": {
            "scientific_explanation": (
                "Facial lines and wrinkles (rhytides) form through a combination of intrinsic biological "
                "aging and extrinsic factors. Within the middle skin layer (the dermis), specialized cells "
                "called fibroblasts synthesize collagen and elastin—the structural proteins that give skin "
                "firmness and elastic recoil. Over time, collagen production naturally slows down, while "
                "enzymes called Matrix Metalloproteinases (MMPs) gradually break down existing collagen "
                "bundles. Sunlight (ultraviolet radiation) generates reactive oxygen species (ROS) that "
                "greatly accelerate this breakdown—a process called photoaging. Repeated facial expressions "
                "(such as smiling or squinting) create dynamic lines that, as supportive dermal elasticity "
                "declines, gradually transition into visible static lines present at rest."
            ),
            "contributing_factors": [
                "Natural chronological aging and slower cellular renewal",
                "Cumulative ultraviolet (UV) radiation accelerating collagen breakdown",
                "Repeated facial muscle expressions (smiling, frowning, squinting)",
                "Gradual depletion of natural hyaluronic acid and dermal moisture",
                "Environmental stressors including dry indoor air, smoking, and pollution",
            ],
            "limitations": (
                "A standard 2D digital photograph captures surface shadows and light reflections; it cannot "
                "measure physical dermal thickness, collagen density, or 3D groove depth in millimeters. "
                "Hydration and facial muscle expression at the instant of photo capture strongly alter line visibility."
            ),
            "source_ids": ["SRC-14", "SRC-17", "SRC-16", "SRC-27"],
            "safety_guidance": (
                "Fine lines are a natural reflection of life and facial expression. Daily broad-spectrum "
                "sunscreen is the most scientifically proven method to protect existing dermal collagen. "
                "For medical anti-aging concerns, consult a board-certified dermatologist."
            ),
        },
    },
}


# Fallback / Inconclusive low confidence entry
INCONCLUSIVE_XAI_KNOWLEDGE = {
    "concept": "inconclusive",
    "display_name": "Inconclusive Pattern",
    "level1": {
        "what_we_noticed": (
            "The photo did not show a clear or pronounced visual skin concern in this area."
        ),
        "where_we_noticed_it_template": "Across the {region_name} area.",
        "why_ai_identified_it": (
            "The AI evaluated the colors, texture, and brightness in this area, but the visual features "
            "did not reach the certainty threshold required to suggest a specific concern pattern."
        ),
        "why_it_can_occur": (
            "Skin in this area may have a relatively uniform surface appearance, or the photo lighting "
            "and resolution may not show distinct surface characteristics. Inconclusive results mean no "
            "strong pattern was detected."
        ),
    },
    "heatmap": {
        "explanation": (
            "Because no dominant pattern reached certainty, the visual focus overlay reflects low "
            "overall activation. This is an informational aid confirming that features were weak."
        ),
    },
    "learn_more": {
        "scientific_explanation": (
            "Computer vision models evaluate local gradient, texture variance, and chromatic distribution. "
            "When feature activations remain below confidence thresholds, scientific responsibility "
            "dictates classifying the pattern as inconclusive rather than forcing an uncertain label. "
            "Research in dermatology AI emphasizes that declaring uncertainty prevents misleading "
            "over-interpretation of normal, healthy skin or ambiguous lighting artifacts."
        ),
        "contributing_factors": [
            "Relatively uniform, healthy skin surface texture",
            "Diffuse ambient lighting without sharp local shadows",
            "Subtle or mild visual characteristics that do not match specific concern clusters",
        ],
        "limitations": (
            "An inconclusive result does not guarantee absence of underlying skin conditions; it simply "
            "means the 2D photographic features did not show a distinct pattern for the 8 trained classes."
        ),
        "source_ids": ["SRC-22", "SRC-24", "SRC-29"],
        "safety_guidance": (
            "Continue gentle daily skin care and broad-spectrum sun protection. If you have personal "
            "skin concerns that are not visible in photos, consult a healthcare professional in person."
        ),
    },
}


SKIN_TYPE_METHODOLOGY = {
    "status": "unavailable",
    "short_explanation": (
        "Skin type determination (dry, oily, combination) requires physical contact measurements "
        "of skin oil and moisture, which cannot be measured from a camera photo."
    ),
    "scientific_rationale": (
        "Clinical dermatological research (Youn et al. 2002, 2005; Mercurio et al. 2013; Seo et al. 2021) "
        "demonstrates that visual appearance alone does not match true physiological sebum secretion. "
        "Valid skin typing requires non-invasive physical instruments: a Sebumeter to measure lipid mass, "
        "a Corneometer to measure stratum corneum hydration, and a Tewameter to measure barrier moisture "
        "loss. Because consumer smartphone cameras lack biophysical contact sensors, DermaLens does not "
        "generate an unvalidated skin type verdict."
    ),
    "supporting_sources": ["SRC-05", "SRC-06", "SRC-07", "SRC-26A"],
}


def build_xai_response(
    region_key: str,
    predicted_concern: Optional[str],
    confidence: float,
    is_confident: bool,
) -> dict[str, Any]:
    """Build structured, two-level XAI explanation for a specific facial region prediction.

    Returns:
        Structured dictionary containing Level 1 (everyday language), Heatmap explanation,
        and Level 2 (Learn More scientific background) with verified source metadata.
    """
    human_region = REGION_HUMAN_NAMES.get(region_key, region_key.replace("_", " "))

    if not predicted_concern or not is_confident or predicted_concern not in XAI_CONCERNS_KNOWLEDGE:
        entry = INCONCLUSIVE_XAI_KNOWLEDGE
        concept_name = entry["concept"]
        display_name = entry["display_name"]
    else:
        entry = XAI_CONCERNS_KNOWLEDGE[predicted_concern]
        concept_name = entry["concept"]
        display_name = entry["display_name"]

    level1_data = entry["level1"]
    where_text = level1_data["where_we_noticed_it_template"].format(region_name=human_region)

    learn_more_data = entry["learn_more"]
    source_objs = get_sources_for_concern(learn_more_data["source_ids"])

    return {
        "concept": concept_name,
        "display_name": display_name,
        "model_confidence": round(confidence, 4),
        "confidence_status": "possible_pattern" if is_confident else "inconclusive_pattern",
        "region": {
            "name": region_key,
            "display_name": human_region.title(),
        },
        "xai": {
            "what_we_noticed": level1_data["what_we_noticed"],
            "where_we_noticed_it": where_text,
            "why_ai_identified_it": level1_data["why_ai_identified_it"],
            "why_it_can_occur": level1_data["why_it_can_occur"],
            "heatmap_explanation": entry["heatmap"]["explanation"],
            "learn_more": {
                "scientific_explanation": learn_more_data["scientific_explanation"],
                "contributing_factors": learn_more_data["contributing_factors"],
                "limitations": learn_more_data["limitations"],
                "safety_guidance": learn_more_data["safety_guidance"],
                "sources": [
                    {
                        "id": s["id"],
                        "title": s["title"],
                        "authors": s["authors"],
                        "year": s["year"],
                        "authority": s["authority"],
                        "identifier": s["identifier"],
                        "url": s["url"],
                        "key_findings": s["key_findings"],
                        "limitations": s["limitations"],
                    }
                    for s in source_objs
                ],
            },
        },
    }
