from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import init_db_indexes
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MongoDB collections and indexes
    init_db_indexes()
    yield


import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend API for the Face Skin Assessment System",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled server error on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred. Please try again later."},
    )


# CORS — allow frontend during development and production from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_and_cache_control_middleware(request: Request, call_next):
    response = await call_next(request)

    path = request.url.path
    # Set strict anti-caching headers for sensitive personal biometric & auth endpoints
    sensitive_prefixes = (
        "/api/v1/auth/me",
        "/api/v1/assessments",
        "/api/v1/results",
        "/api/v1/xai",
    )
    if any(path.startswith(prefix) for prefix in sensitive_prefixes):
        response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    # Defense-in-depth standard security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

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