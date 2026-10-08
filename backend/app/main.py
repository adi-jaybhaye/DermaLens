from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.assessments import router as assessment_router
from app.api.routes.images import router as image_router
from app.api.routes.quality import router as quality_router
from app.api.routes.face import router as face_router
from app.api.routes.skin import router as skin_router
from app.api.routes.results import router as results_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.sources import router as sources_router
from app.api.routes.xai import router as xai_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend API for the Face Skin Assessment System",
)

# CORS — allow frontend during development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication & Identity
app.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["Authentication"],
)

# System Health
app.include_router(
    health_router,
    prefix="/api/v1",
    tags=["Health"],
)

# Assessment Management
app.include_router(
    assessment_router,
    prefix="/api/v1",
    tags=["Assessments"],
)

# Image Ingestion & Processing
app.include_router(
    image_router,
    prefix="/api/v1",
    tags=["Images"],
)

# Image Quality Assessment
app.include_router(
    quality_router,
    prefix="/api/v1",
    tags=["Image Quality"],
)

# Face Processing & Landmarks
app.include_router(
    face_router,
    prefix="/api/v1",
    tags=["Face Analysis"],
)

# Skin Concern Inference
app.include_router(
    skin_router,
    prefix="/api/v1",
    tags=["Skin Analysis"],
)

# Results & Synthesis
app.include_router(
    results_router,
    prefix="/api/v1",
    tags=["Results"],
)

# Curated Scientific Knowledge
app.include_router(
    knowledge_router,
    prefix="/api/v1",
    tags=["Knowledge"],
)

# Dermatological Evidence Sources
app.include_router(
    sources_router,
    prefix="/api/v1",
    tags=["Sources"],
)

# Explainable AI (Grad-CAM)
app.include_router(
    xai_router,
    prefix="/api/v1",
    tags=["Explainable AI"],
)


from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Serve static frontend build if present
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "message": "Face Skin Assessment API is running",
            "version": "1.0.0",
            "docs_url": "/docs",
        }