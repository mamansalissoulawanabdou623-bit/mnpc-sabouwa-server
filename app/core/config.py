from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ==========================================
    # APPLICATION
    # ==========================================

    app_name: str = Field(
        default="MNPC SABOUWA API",
        validation_alias="APP_NAME",
    )

    app_env: str = Field(
        default="development",
        validation_alias="APP_ENV",
    )

    debug: bool = Field(
        default=True,
        validation_alias="DEBUG",
    )


    # ==========================================
    # BASE DE DONNEES
    # ==========================================

    database_url: str = Field(
        default=(
            "postgresql+psycopg://"
            "postgres:password@localhost:5432/mnpc_sabouwa"
        ),
        validation_alias="DATABASE_URL",
    )


    # ==========================================
    # JWT / SECURITE
    # ==========================================

    secret_key: str = Field(
        default="CHANGE_THIS_SECRET_KEY",
        validation_alias="JWT_SECRET_KEY",
    )

    algorithm: str = "HS256"

    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="JWT_ACCESS_MINUTES",
    )

    refresh_token_expire_days: int = Field(
        default=30,
        validation_alias="JWT_REFRESH_DAYS",
    )


    # ==========================================
    # VERIFICATION EMAIL
    # ==========================================

    verification_code_minutes: int = Field(
        default=10,
        validation_alias="VERIFICATION_CODE_MINUTES",
    )

    verification_max_attempts: int = Field(
        default=5,
        validation_alias="VERIFICATION_MAX_ATTEMPTS",
    )


    # ==========================================
    # EMAIL / RESEND
    # ==========================================

    email_mode: str = Field(
        default="console",
        validation_alias="EMAIL_MODE",
    )

    resend_api_key: str = Field(
        default="",
        validation_alias="RESEND_API_KEY",
    )

    resend_from_email: str = Field(
        default="onboarding@resend.dev",
        validation_alias="RESEND_FROM_EMAIL",
    )

    resend_from_name: str = Field(
        default="MNPC SABOUWA",
        validation_alias="RESEND_FROM_NAME",
    )


    # ==========================================
    # SMTP
    # Conservé pour compatibilité
    # ==========================================

    smtp_host: str = Field(
        default="",
        validation_alias="SMTP_HOST",
    )

    smtp_port: int = Field(
        default=587,
        validation_alias="SMTP_PORT",
    )

    smtp_username: str = Field(
        default="",
        validation_alias="SMTP_USERNAME",
    )

    smtp_password: str = Field(
        default="",
        validation_alias="SMTP_PASSWORD",
    )

    smtp_from_email: str = Field(
        default="",
        validation_alias="SMTP_FROM_EMAIL",
    )

    smtp_from_name: str = Field(
        default="MNPC SABOUWA",
        validation_alias="SMTP_FROM_NAME",
    )

    smtp_use_ssl: bool = Field(
        default=False,
        validation_alias="SMTP_USE_SSL",
    )


    # ==========================================
    # CORS
    # ==========================================

    cors_origins: str = Field(
        default="*",
        validation_alias="CORS_ORIGINS",
    )


    # ==========================================
    # CONFIGURATION PYDANTIC
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


    @property
    def cors_origin_list(self) -> list[str]:

        if self.cors_origins.strip() == "*":
            return ["*"]

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()