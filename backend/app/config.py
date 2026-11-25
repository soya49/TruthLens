import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./truthlens.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-development-secret")
    jwt_expiry_minutes: int = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ai_provider: str = os.getenv("AI_PROVIDER", "none")
    ai_api_key: str | None = os.getenv("AI_API_KEY")
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", "10485760"))

    def __post_init__(self) -> None:
        if self.environment.lower() == "production" and self.jwt_secret == "change-this-development-secret":
            raise RuntimeError("JWT_SECRET must be configured in production.")


settings = Settings()
