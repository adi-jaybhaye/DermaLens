"""
Curated skin concern knowledge base.

Each entry provides evidence-based information for one of the 8 concern
classes recognised by the EfficientNet-B0 model trained on Dataset A.

IMPORTANT:
- This data is curated from authoritative dermatological sources.
- It does NOT constitute medical advice or diagnosis.
- The AI model identifies visible patterns; these entries explain what
  those patterns can be associated with, not what caused them in a
  specific individual.
"""

SKIN_CONCERNS_KNOWLEDGE = {
    # ------------------------------------------------------------------
    # 1. Redness
    # ------------------------------------------------------------------
    "Redness": {
        "concept": "Redness",
        "display_name": "Redness (Erythema)",
        "description": (
            "Visible reddening or flushing of the skin surface. "
            "Erythema can appear as diffuse redness, localised patches, "
            "or visible blood vessels near the skin surface."
        ),
        "visual_characteristics": [
            "Red or pink patches on the skin",
            "Diffuse flushing across affected areas",
            "Visible small blood vessels (telangiectasia)",
            "Skin may appear warm or irritated",
        ],
        "common_contributing_factors": [
            "Sun exposure and UV damage",
            "Temperature extremes (heat or cold)",
            "Skin sensitivity or barrier impairment",
            "Contact with irritants or allergens",
            "Rosacea or related conditions",
            "Hormonal fluctuations",
            "Certain medications or topical products",
        ],
        "why_it_can_occur": (
            "Redness is commonly associated with dilation of blood "
            "vessels near the skin surface (vasodilation) and increased "
            "blood flow. This can result from inflammatory processes, "
            "environmental triggers, or underlying skin conditions. "
            "An image alone cannot determine the exact cause of redness."
        ),
        "safety_notes": (
            "Persistent or worsening redness, redness accompanied by "
            "pain, swelling, warmth, or spreading beyond the original "
            "area may warrant professional evaluation."
        ),
        "when_to_consult": (
            "Consider consulting a dermatologist if redness is "
            "persistent, recurrent, progressively worsening, or "
            "accompanied by other symptoms such as burning, stinging, "
            "or visible blood vessels."
        ),
        "evidence_references": [
            {
                "title": "Rosacea: Diagnosis and Treatment",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/diseases/rosacea",
            },
            {
                "title": "Erythema — Clinical Overview",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/erythema",
            },
            {
                "title": "Rosacea",
                "source": "Mayo Clinic",
                "url": "https://www.mayoclinic.org/diseases-conditions/rosacea/symptoms-causes/syc-20353815",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 2. Dark Spots
    # ------------------------------------------------------------------
    "dark spots": {
        "concept": "dark spots",
        "display_name": "Dark Spots (Hyperpigmentation)",
        "description": (
            "Localised areas of skin that appear darker than the "
            "surrounding skin. Dark spots are a common form of "
            "hyperpigmentation caused by excess melanin production."
        ),
        "visual_characteristics": [
            "Flat, darkened patches or spots",
            "Well-defined or diffuse borders",
            "Brown, dark brown, or greyish discolouration",
            "Varying sizes from small dots to larger patches",
        ],
        "common_contributing_factors": [
            "Cumulative sun exposure (UV radiation)",
            "Post-inflammatory hyperpigmentation (after acne or injury)",
            "Hormonal changes (pregnancy, contraceptives)",
            "Natural skin aging (age spots / solar lentigines)",
            "Genetic predisposition",
            "Skin injuries or friction",
        ],
        "why_it_can_occur": (
            "Dark spots typically result from excess melanin production "
            "by melanocytes. UV exposure stimulates melanin synthesis as "
            "a protective response. Inflammation from acne, wounds, or "
            "irritation can also trigger post-inflammatory "
            "hyperpigmentation. An image alone cannot determine the "
            "exact cause of dark spots."
        ),
        "safety_notes": (
            "Most dark spots are benign. However, any spot that changes "
            "in size, shape, colour, or becomes irregular should be "
            "evaluated by a dermatologist to rule out other conditions."
        ),
        "when_to_consult": (
            "Consult a dermatologist if dark spots change in "
            "appearance, have irregular borders, bleed, itch, or are "
            "accompanied by other skin changes."
        ),
        "evidence_references": [
            {
                "title": "Dark Spots: Causes and Treatment",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/cosmetic/skin-care/dark-spots",
            },
            {
                "title": "Solar Lentigo",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/solar-lentigo",
            },
            {
                "title": "Hyperpigmentation",
                "source": "Cleveland Clinic",
                "url": "https://my.clevelandclinic.org/health/diseases/21885-hyperpigmentation",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 3. Inflammatory Acne
    # ------------------------------------------------------------------
    "inflammatory acne": {
        "concept": "inflammatory acne",
        "display_name": "Inflammatory Acne",
        "description": (
            "Acne lesions characterised by redness, swelling, and "
            "inflammation. Includes papules (red bumps), pustules "
            "(bumps containing pus), and potentially deeper nodules."
        ),
        "visual_characteristics": [
            "Red, swollen bumps (papules)",
            "Pus-filled lesions (pustules)",
            "Tender or painful to touch",
            "Surrounding redness and inflammation",
            "Possible scarring from healed lesions",
        ],
        "common_contributing_factors": [
            "Excess sebum (oil) production",
            "Proliferation of Cutibacterium acnes bacteria",
            "Hormonal fluctuations (puberty, menstrual cycle)",
            "Clogged hair follicles (dead skin cells and oil)",
            "Stress and lifestyle factors",
            "Certain dietary factors",
            "Genetic predisposition",
        ],
        "why_it_can_occur": (
            "Inflammatory acne develops when clogged hair follicles "
            "become infected with bacteria (primarily C. acnes). The "
            "immune system responds with an inflammatory cascade, "
            "causing redness, swelling, and pus formation. Hormonal "
            "changes can increase sebum production, contributing to "
            "the cycle. An image alone cannot determine the exact "
            "cause or severity of acne."
        ),
        "safety_notes": (
            "Severe or persistent inflammatory acne can lead to "
            "scarring. Avoid picking or squeezing lesions as this "
            "can worsen inflammation and increase scarring risk."
        ),
        "when_to_consult": (
            "Consult a dermatologist if acne is severe, painful, "
            "leaving scars, not responding to over-the-counter "
            "treatments, or significantly affecting quality of life."
        ),
        "evidence_references": [
            {
                "title": "Acne: Overview",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/diseases/acne",
            },
            {
                "title": "Acne",
                "source": "National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIAMS)",
                "url": "https://www.niams.nih.gov/health-topics/acne",
            },
            {
                "title": "Acne Vulgaris",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/acne-vulgaris",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 4. Non-inflammatory Acne — Blackheads
    # ------------------------------------------------------------------
    "non inflammatory acne black heads": {
        "concept": "non inflammatory acne black heads",
        "display_name": "Blackheads (Open Comedones)",
        "description": (
            "Small, dark-coloured bumps on the skin surface caused by "
            "clogged hair follicles. The dark colour results from "
            "oxidation of the follicle contents when exposed to air, "
            "not from dirt."
        ),
        "visual_characteristics": [
            "Small dark or black dots on the skin surface",
            "Slightly raised or flat",
            "Commonly found on the nose, chin, and forehead",
            "Open pore visible at the surface",
            "Non-inflamed (no redness or swelling)",
        ],
        "common_contributing_factors": [
            "Excess sebum production",
            "Accumulation of dead skin cells in follicles",
            "Hormonal changes",
            "Use of comedogenic (pore-clogging) products",
            "Environmental factors (humidity, pollution)",
            "Genetic predisposition to oilier skin",
        ],
        "why_it_can_occur": (
            "Blackheads form when a hair follicle becomes clogged "
            "with sebum and dead skin cells. Unlike whiteheads, the "
            "follicle remains open at the surface. The exposed "
            "contents undergo oxidation (exposure to air), which "
            "causes the characteristic dark appearance. The dark "
            "colour is from melanin oxidation, not dirt. An image "
            "alone cannot determine the exact contributing factors."
        ),
        "safety_notes": (
            "Blackheads are generally a mild form of acne. Avoid "
            "aggressive extraction or squeezing, which can damage "
            "the skin and potentially cause inflammation or scarring."
        ),
        "when_to_consult": (
            "Consider consulting a dermatologist if blackheads are "
            "widespread, persistent despite consistent skincare, or "
            "if you are unsure about appropriate treatment options."
        ),
        "evidence_references": [
            {
                "title": "Comedonal Acne",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/comedonal-acne",
            },
            {
                "title": "Acne: Who Gets and Causes",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/diseases/acne/causes/acne-causes",
            },
            {
                "title": "Acne — Symptoms and Causes",
                "source": "Mayo Clinic",
                "url": "https://www.mayoclinic.org/diseases-conditions/acne/symptoms-causes/syc-20368047",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 5. Non-inflammatory Acne — Whiteheads
    # ------------------------------------------------------------------
    "non inflammatory acne white heads": {
        "concept": "non inflammatory acne white heads",
        "display_name": "Whiteheads (Closed Comedones)",
        "description": (
            "Small, flesh-coloured or white bumps caused by clogged "
            "hair follicles that remain closed at the skin surface. "
            "Unlike blackheads, the follicle opening is sealed."
        ),
        "visual_characteristics": [
            "Small, dome-shaped bumps",
            "Flesh-coloured, white, or slightly yellowish",
            "No visible pore opening at the surface",
            "Non-inflamed (no significant redness)",
            "Commonly found on the forehead, chin, and cheeks",
        ],
        "common_contributing_factors": [
            "Excess sebum production",
            "Dead skin cell accumulation within follicles",
            "Hormonal fluctuations",
            "Comedogenic skincare or cosmetic products",
            "Genetic predisposition",
        ],
        "why_it_can_occur": (
            "Whiteheads form when a hair follicle becomes clogged "
            "with sebum and dead skin cells, and the follicle "
            "opening remains closed. Because the contents are not "
            "exposed to air, oxidation does not occur and the bump "
            "retains a white or flesh-coloured appearance. An image "
            "alone cannot determine the exact contributing factors."
        ),
        "safety_notes": (
            "Whiteheads are a mild form of acne. Attempting to "
            "squeeze or pop them can push contents deeper into the "
            "skin, potentially causing inflammation and scarring."
        ),
        "when_to_consult": (
            "Consider consulting a dermatologist if whiteheads are "
            "widespread, persistent, or if they begin to develop "
            "into inflamed lesions."
        ),
        "evidence_references": [
            {
                "title": "Comedonal Acne",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/comedonal-acne",
            },
            {
                "title": "Acne: Types",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/diseases/acne/really-acne/types",
            },
            {
                "title": "Acne",
                "source": "Cleveland Clinic",
                "url": "https://my.clevelandclinic.org/health/diseases/12233-acne",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 6. Pigmentation
    # ------------------------------------------------------------------
    "pigmentation": {
        "concept": "pigmentation",
        "display_name": "Uneven Pigmentation",
        "description": (
            "Irregular distribution of skin colour, resulting in "
            "patches that are darker or lighter than the surrounding "
            "skin. This encompasses various pigmentation disorders "
            "including melasma and post-inflammatory changes."
        ),
        "visual_characteristics": [
            "Patches of varying skin darkness",
            "Uneven or mottled skin tone",
            "Brown, tan, or greyish patches",
            "Often symmetrical distribution (in melasma)",
            "May affect sun-exposed areas more prominently",
        ],
        "common_contributing_factors": [
            "Chronic sun exposure (UV radiation)",
            "Hormonal influences (pregnancy, oral contraceptives)",
            "Post-inflammatory changes from skin injury",
            "Genetic predisposition and skin type",
            "Aging and cumulative photoaging",
            "Certain medications",
        ],
        "why_it_can_occur": (
            "Uneven pigmentation results from irregular melanin "
            "distribution across the skin. Melanocytes (melanin-"
            "producing cells) can become overactive in certain areas "
            "due to UV stimulation, hormonal signals, or inflammatory "
            "triggers. Photoaging from cumulative sun exposure is one "
            "of the most common contributing factors. An image alone "
            "cannot determine the exact cause of pigmentation changes."
        ),
        "safety_notes": (
            "Most pigmentation changes are cosmetic. However, new or "
            "changing pigmented lesions should be evaluated to rule "
            "out other conditions."
        ),
        "when_to_consult": (
            "Consult a dermatologist if pigmentation is new, "
            "rapidly changing, asymmetrical, or accompanied by "
            "other symptoms. Melasma and other pigmentation "
            "disorders may benefit from professional treatment."
        ),
        "evidence_references": [
            {
                "title": "Melasma: Overview",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/diseases/a-z/melasma-overview",
            },
            {
                "title": "Disorders of Pigmentation",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/disorders-of-pigmentation",
            },
            {
                "title": "Hyperpigmentation",
                "source": "British Association of Dermatologists",
                "url": "https://www.bad.org.uk/pils/pigmentation-disorders/",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 7. Pores
    # ------------------------------------------------------------------
    "pores": {
        "concept": "pores",
        "display_name": "Enlarged Pores",
        "description": (
            "Visibly enlarged pore openings on the skin surface. "
            "While all skin has pores, they can become more "
            "prominent due to various factors affecting sebum "
            "production and skin elasticity."
        ),
        "visual_characteristics": [
            "Visible pore openings, especially in the T-zone",
            "Orange-peel texture on affected areas",
            "Most prominent on the nose, cheeks, and forehead",
            "Skin may appear oily or shiny in affected areas",
        ],
        "common_contributing_factors": [
            "Excess sebum (oil) production",
            "Reduced skin elasticity with aging",
            "Cumulative sun damage (loss of collagen support)",
            "Genetic predisposition",
            "Clogged pores (debris stretching the opening)",
            "Hormonal influences",
        ],
        "why_it_can_occur": (
            "Pores become visibly enlarged when sebaceous glands "
            "produce excess oil, causing the pore opening to dilate. "
            "Loss of collagen and elastin due to aging or sun damage "
            "reduces the structural support around pores, making them "
            "appear larger. Debris accumulation within pores can also "
            "stretch the opening. An image alone cannot determine "
            "the exact contributing factors."
        ),
        "safety_notes": (
            "Enlarged pores are primarily a cosmetic concern and do "
            "not typically indicate a medical condition. Avoid "
            "aggressive pore-clearing methods that can damage the "
            "skin."
        ),
        "when_to_consult": (
            "Consider consulting a dermatologist if enlarged pores "
            "are a cosmetic concern and you would like professional "
            "guidance on skincare or treatment options."
        ),
        "evidence_references": [
            {
                "title": "How to Minimise Pores",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/cosmetic/younger-looking/how-to-minimize-pores",
            },
            {
                "title": "Enlarged Pores",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/enlarged-pores",
            },
            {
                "title": "Pores: What Are They and How to Care for Them",
                "source": "Cleveland Clinic",
                "url": "https://my.clevelandclinic.org/health/body/22729-pores",
            },
        ],
    },

    # ------------------------------------------------------------------
    # 8. Wrinkles
    # ------------------------------------------------------------------
    "wrinkles": {
        "concept": "wrinkles",
        "display_name": "Wrinkles and Fine Lines",
        "description": (
            "Lines, creases, and folds that develop in the skin over "
            "time. Fine lines are shallow and often the earliest sign "
            "of aging; deeper wrinkles are more pronounced creases."
        ),
        "visual_characteristics": [
            "Fine lines around the eyes (crow's feet)",
            "Forehead lines and furrows",
            "Nasolabial folds (nose to mouth lines)",
            "Skin texture appears less smooth",
            "Loss of skin firmness and elasticity",
        ],
        "common_contributing_factors": [
            "Natural aging (intrinsic aging)",
            "Cumulative sun exposure (photoaging)",
            "Repeated facial expressions",
            "Smoking and tobacco use",
            "Reduced collagen and elastin production",
            "Dehydration and moisture loss",
            "Genetic predisposition",
            "Environmental factors (pollution, wind)",
        ],
        "why_it_can_occur": (
            "Wrinkles develop through a gradual loss of collagen "
            "and elastin — the structural proteins that maintain "
            "skin firmness and elasticity. UV exposure accelerates "
            "this process (photoaging) by breaking down collagen "
            "fibres. Decreased cell turnover and reduced moisture "
            "retention with age further contribute to wrinkle "
            "formation. Repeated muscle contractions from facial "
            "expressions create dynamic lines that can become "
            "permanent over time. An image alone cannot determine "
            "the exact cause of wrinkles."
        ),
        "safety_notes": (
            "Wrinkles are a natural part of aging. Sudden or "
            "unusual skin texture changes unrelated to aging should "
            "be evaluated by a professional."
        ),
        "when_to_consult": (
            "Consider consulting a dermatologist if you are "
            "interested in professional anti-aging treatments, "
            "or if skin changes appear unusual or are accompanied "
            "by other symptoms."
        ),
        "evidence_references": [
            {
                "title": "Wrinkles: Causes and Prevention",
                "source": "American Academy of Dermatology (AAD)",
                "url": "https://www.aad.org/public/cosmetic/younger-looking/causes-of-wrinkles",
            },
            {
                "title": "Wrinkles",
                "source": "Mayo Clinic",
                "url": "https://www.mayoclinic.org/diseases-conditions/wrinkles/symptoms-causes/syc-20354927",
            },
            {
                "title": "Ageing and the Skin",
                "source": "DermNet NZ",
                "url": "https://dermnetnz.org/topics/skin-ageing",
            },
        ],
    },
}


# Safety disclaimer text used across the application.
SAFETY_DISCLAIMER = {
    "disclaimer": (
        "This assessment is for informational and educational purposes "
        "only. It does not constitute medical advice, diagnosis, or "
        "treatment. The visual analysis identifies surface patterns in images "
        "and does not determine clinical causes. Results should not "
        "replace professional dermatological consultation."
    ),
    "model_info": {
        "name": "EfficientNet-B0",
        "dataset": "Dataset A (8 skin concern classes)",
        "validation_accuracy": 0.9289,
        "accuracy_note": (
            "This is validation accuracy on the training dataset "
            "split only. It does not represent clinical, diagnostic, "
            "or real-world accuracy."
        ),
        "region_note": (
            "Region-level analysis applies the trained model to "
            "facial region crops. This approach has not been "
            "independently validated and the reported validation "
            "accuracy does not apply to individual facial regions."
        ),
    },
    "recommendation": (
        "If you have concerns about your skin health, please consult "
        "a qualified dermatologist or healthcare professional."
    ),
}
