from fastapi import APIRouter

from app.config.database import check_database_connection


router = APIRouter()


@router.get("/health")
def health_check():
    database_connected = check_database_connection()

    return {
        "status": "ok" if database_connected else "degraded",
        "service": "face-skin-assessment-api",
        "database": "connected" if database_connected else "disconnected",
    }