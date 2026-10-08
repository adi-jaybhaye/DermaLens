import hashlib
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from app.data.skin_concerns_knowledge import SKIN_CONCERNS_KNOWLEDGE

router = APIRouter()


def _get_all_sources() -> Dict[str, Dict[str, Any]]:
    """Compile a registry of all referenced sources with unique deterministic IDs."""
    sources: Dict[str, Dict[str, Any]] = {}
    for concern_key, concern_data in SKIN_CONCERNS_KNOWLEDGE.items():
        refs = concern_data.get("evidence_references", [])
        for ref in refs:
            # Deterministic ID based on URL or title
            seed = ref.get("url") or ref.get("title", "")
            source_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
            if source_id not in sources:
                sources[source_id] = {
                    "id": source_id,
                    "title": ref.get("title"),
                    "source": ref.get("source"),
                    "url": ref.get("url"),
                    "related_concerns": [concern_data.get("display_name", concern_key)],
                }
            else:
                display_name = concern_data.get("display_name", concern_key)
                if display_name not in sources[source_id]["related_concerns"]:
                    sources[source_id]["related_concerns"].append(display_name)
    return sources


@router.get("/sources")
def list_sources():
    """Return all curated scientific and dermatological sources."""
    all_sources = list(_get_all_sources().values())
    return {
        "sources": all_sources,
        "total": len(all_sources),
    }


@router.get("/sources/{source_id}")
def get_source(source_id: str):
    """Retrieve details for a specific dermatological source by ID."""
    all_sources = _get_all_sources()
    if source_id not in all_sources:
        raise HTTPException(
            status_code=404,
            detail=f"Source with ID '{source_id}' not found",
        )
    return all_sources[source_id]
