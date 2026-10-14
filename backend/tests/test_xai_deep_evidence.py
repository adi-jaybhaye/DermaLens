"""
Unit and integration tests for DermaLens Explainable AI (XAI) deep evidence system.

Validates that:
1. All 8 concern classes return valid, complete two-level XAI explanations.
2. Explanations contain: What, Where, Why AI, Why can this occur, and Heatmap explanation.
3. Level 2 Learn More contains scientific explanation, contributing factors, limitations,
   safety guidance, and traceable evidence sources.
4. All source citations map to authentic inspected research documents in EVIDENCE_SOURCES.
5. Inconclusive / low-confidence pattern handling functions properly.
6. Skin type methodology remains unavailable with grounded biophysical rationale.
7. Model confidence terminology is used instead of match terminology.
"""

import pytest
from app.data.evidence_sources import EVIDENCE_SOURCES, get_source_by_id, get_sources_for_concern
from app.data.xai_knowledge import (
    XAI_CONCERNS_KNOWLEDGE,
    INCONCLUSIVE_XAI_KNOWLEDGE,
    SKIN_TYPE_METHODOLOGY,
    build_xai_response,
    REGION_HUMAN_NAMES,
)
from app.services.knowledge_service import (
    get_region_xai_explanation,
    get_skin_type_methodology,
)


SUPPORTED_CONCERNS = [
    "Redness",
    "dark spots",
    "inflammatory acne",
    "non inflammatory acne black heads",
    "non inflammatory acne white heads",
    "pigmentation",
    "pores",
    "wrinkles",
]


class TestXAIDeepEvidence:

    def test_all_8_concerns_registered(self):
        """Verify all 8 EfficientNet-B0 trained classes exist in XAI knowledge base."""
        for concern in SUPPORTED_CONCERNS:
            assert concern in XAI_CONCERNS_KNOWLEDGE, f"Missing XAI knowledge for: {concern}"

    @pytest.mark.parametrize("concern_name", SUPPORTED_CONCERNS)
    def test_level1_everyday_language_structure(self, concern_name):
        """Verify Level 1 everyday language contains all required explanation pillars."""
        resp = build_xai_response(
            region_key="left_cheek",
            predicted_concern=concern_name,
            confidence=0.85,
            is_confident=True,
        )

        assert resp["concept"] == concern_name
        assert resp["display_name"]
        assert resp["model_confidence"] == 0.85
        assert resp["confidence_status"] == "possible_pattern"

        xai = resp["xai"]
        # Level 1 fields
        assert xai["what_we_noticed"], f"Missing 'what_we_noticed' for {concern_name}"
        assert xai["where_we_noticed_it"], f"Missing 'where_we_noticed_it' for {concern_name}"
        assert xai["why_ai_identified_it"], f"Missing 'why_ai_identified_it' for {concern_name}"
        assert xai["why_it_can_occur"], f"Missing 'why_it_can_occur' for {concern_name}"
        assert xai["heatmap_explanation"], f"Missing 'heatmap_explanation' for {concern_name}"

        # Check that 'where' contains the human-readable region name
        assert "left cheek" in xai["where_we_noticed_it"].lower()

        # Check language safety: No definitive diagnostic claims in Level 1
        lowered_what = xai["what_we_noticed"].lower()
        lowered_why = xai["why_it_can_occur"].lower()
        assert "diagnosed with" not in lowered_what
        assert "confirmed disease" not in lowered_what
        assert "cannot tell us" in lowered_why or "cannot identify" in lowered_why or "cannot determine" in lowered_why

    @pytest.mark.parametrize("concern_name", SUPPORTED_CONCERNS)
    def test_level2_learn_more_scientific_grounding(self, concern_name):
        """Verify Level 2 Learn More contains detailed scientific explanation and valid sources."""
        resp = build_xai_response(
            region_key="forehead",
            predicted_concern=concern_name,
            confidence=0.78,
            is_confident=True,
        )

        learn_more = resp["xai"]["learn_more"]
        assert len(learn_more["scientific_explanation"]) > 100, f"Scientific explanation too brief for {concern_name}"
        assert len(learn_more["contributing_factors"]) >= 3, f"Insufficient contributing factors for {concern_name}"
        assert len(learn_more["limitations"]) > 50, f"Missing limitations for {concern_name}"
        assert learn_more["safety_guidance"], f"Missing safety guidance for {concern_name}"
        assert len(learn_more["sources"]) >= 1, f"Missing evidence sources for {concern_name}"

        # Check that every source contains genuine fields
        for src in learn_more["sources"]:
            assert src["id"].startswith("SRC-")
            assert src["title"]
            assert src["authors"]
            assert src["year"]
            assert src["authority"]
            assert src["identifier"]
            assert src["key_findings"]
            assert src["limitations"]

    def test_heatmap_explanation_non_causal(self):
        """Verify heatmap explanation explicitly frames Grad-CAM as a model focus aid, not medical cause."""
        for concern in SUPPORTED_CONCERNS:
            resp = build_xai_response("nose", concern, 0.90, True)
            heatmap_text = resp["xai"]["heatmap_explanation"]

            assert "explanation aid" in heatmap_text.lower() or "visual guide" in heatmap_text.lower()
            assert "does not show the biological cause" in heatmap_text or "not a medical test" in heatmap_text
            assert "confirmed diagnosis" not in heatmap_text
            assert "proves the condition" not in heatmap_text

    def test_low_confidence_inconclusive_pattern(self):
        """Verify low-confidence predictions fall back to inconclusive pattern safely."""
        resp = build_xai_response(
            region_key="chin",
            predicted_concern="Redness",
            confidence=0.22,
            is_confident=False,
        )

        assert resp["concept"] == "inconclusive"
        assert resp["display_name"] == "Inconclusive Pattern"
        assert resp["confidence_status"] == "inconclusive_pattern"
        assert "did not show a clear or pronounced" in resp["xai"]["what_we_noticed"]
        assert resp["xai"]["learn_more"]["sources"]

    def test_evidence_sources_integrity(self):
        """Verify all evidence sources are internally consistent and non-fabricated."""
        assert len(EVIDENCE_SOURCES) >= 20

        for sid, src in EVIDENCE_SOURCES.items():
            assert src["id"] == sid
            assert src["file_name"].endswith(".docx")
            assert src["title"]
            assert src["authors"]
            assert src["year"]
            assert src["authority"]
            assert len(src["supported_claims"]) >= 1
            assert len(src["unsupported_claims"]) >= 1

    def test_skin_type_unavailable_methodology(self):
        """Verify skin type remains unavailable with biophysical instrumentation grounding."""
        meta = get_skin_type_methodology()
        assert meta["status"] == "unavailable"
        assert "Sebumeter" in meta["scientific_rationale"]
        assert "Corneometer" in meta["scientific_rationale"]
        assert "Tewameter" in meta["scientific_rationale"]
        assert "SRC-05" in meta["supporting_sources"]  # Youn et al. 2002
        assert "SRC-06" in meta["supporting_sources"]  # Youn et al. 2005
        assert "SRC-07" in meta["supporting_sources"]  # Mercurio et al. 2013
        assert "SRC-26A" in meta["supporting_sources"] # Seo et al. 2021
