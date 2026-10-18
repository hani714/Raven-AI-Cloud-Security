import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RESEND_API_KEY: str
    BREVO_API_KEY: str
    SENTRY_DSN: str
    SENTRY_ENVIRONMENT: str
    DATABASE_URL: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    PADDLE_API_KEY: str
    PADDLE_WEBHOOK_SECRET: str
    REDIS_URL: str
    REDIS_TTL: int
    ENCRYPTION_KEY: str

    class Config:
        # Do not read local .env on Render/production; use platform env vars only.
        env_file = None if os.getenv("RENDER") == "true" else ".env"
        extra = "ignore"

settings = Settings()