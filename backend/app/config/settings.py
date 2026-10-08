from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Face Skin Assessment API"
    environment: str = "development"

    mongodb_uri: str
    mongodb_database: str = "face_skin_assessment"

    # JWT Authentication
    jwt_secret_key: str = "dev_secret_key_change_in_production_face_skin_assessment_2025"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()