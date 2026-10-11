from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Face Skin Assessment API"
    environment: str = "development"

    mongodb_uri: str
    mongodb_database: str = "face_skin_assessment"

    # JWT Authentication
    jwt_secret_key: str = "dev_secret_key_change_in_production_face_skin_assessment_2025"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # CORS configuration (comma-separated origins)
    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:3000"
    )

    # ML Model Configuration
    model_path: str = "training/models/efficientnet_b0_skin_concerns.pth"
    model_version: str = "efficientnet_b0_v1"
    min_confidence_threshold: float = 0.35

    # Storage
    upload_dir: str = "uploads"
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "assessment-images"

    @property
    def allowed_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        if self.environment.lower() == "production":
            if (
                not self.jwt_secret_key
                or "dev_secret" in self.jwt_secret_key
                or "change_in_production" in self.jwt_secret_key
            ):
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production environment, a strong, random "
                    "JWT_SECRET_KEY environment variable must be explicitly configured."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()