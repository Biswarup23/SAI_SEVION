from dotenv import load_dotenv
load_dotenv()  # ensures .env is loaded even during imports (engine/settings)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- environment ----
    ENV: str = "dev"

    # ---- database ----
    DATABASE_URL: str = "sqlite:///./devion.db"

    # ---- OpenAI ----
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # ---- Auth / JWT ----
    JWT_SECRET: str = "CHANGE_THIS"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    VERIFY_TOKEN_EXPIRE_MINUTES: int = 60

    # ---- App base ----
    APP_BASE_URL: str = "http://127.0.0.1:8000"

    # ---- SMTP ----
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_FROM: str = "no-reply@saidevion.local"

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
