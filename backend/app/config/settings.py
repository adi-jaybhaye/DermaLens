from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Face Skin Assessment API"
    environment: str = "development"

    mongodb_uri: str
    mongodb_direct_fallback_uri: str = ""
    mongodb_database: str = "face_skin_assessment"

    # JWT Authentication & Secure Session Cookies
    jwt_secret_key: str = "dev_secret_key_change_in_production_face_skin_assessment_2025"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    cookie_name: str = "derma_session"
    cookie_samesite: str = "lax"

    # CORS configuration (comma-separated origins)
    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:3000,"
        "https://dermalens-backend.azurewebsites.net"
    )

    # ML Model Configuration
    model_path: str = "models/efficientnet_b0_skin_concerns.pth"
    model_version: str = "efficientnet_b0_v1"
    model_checksum: str = "ba123334b476a24b710a78000a70b1d6dcc44ee100664673d6e61ed3d0827412"
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
            # 1. Reject weak or default dev secret
            if (
                not self.jwt_secret_key
                or "dev_secret" in self.jwt_secret_key
                or "change_in_production" in self.jwt_secret_key
                or len(self.jwt_secret_key) < 32
            ):
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production environment, a strong, random "
                    "JWT_SECRET_KEY (min 32 characters) must be explicitly configured."
                )

            # 2. Reject silent local storage fallback in production
            if not self.azure_storage_connection_string or not self.azure_storage_connection_string.strip():
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production environment, AZURE_STORAGE_CONNECTION_STRING "
                    "must be configured. Local disk fallback for private biometric data is prohibited in production."
                )

            # 3. Reject blanket wildcard CORS in production
            if "*" in self.allowed_cors_origins:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production environment, blanket wildcard CORS "
                    "allow_origins=['*'] is strictly prohibited."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
