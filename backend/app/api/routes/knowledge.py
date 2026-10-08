from fastapi import APIRouter, HTTPException

from app.services.knowledge_service import (
    get_all_concerns,
    get_concern,
    get_safety_disclaimer,
)


router = APIRouter()


@router.get("/knowledge")
def list_knowledge():
    """Return all curated skin concern knowledge entries."""
    return {
        "concerns": get_all_concerns(),
        "total": len(get_all_concerns()),
    }


@router.get("/knowledge/{concept}")
def get_knowledge(concept: str):
    """Return knowledge for a specific skin concern concept.

    The concept key must match a model class name exactly
    (e.g. 'Redness', 'dark spots', 'wrinkles').
    """
    data = get_concern(concept)

    if data is None:
        available = [c["concept"] for c in get_all_concerns()]
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Concern '{concept}' not found",
                "available_concepts": available,
            },
        )

    return data


@router.get("/safety")
def get_safety():
    """Return safety disclaimer and model information."""
    return get_safety_disclaimer()
