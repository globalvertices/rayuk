from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://rayuk:rayuk_dev@localhost:5434/rayuk"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Stripe (for credit top-ups)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Storage
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = "./uploads"
    AWS_S3_BUCKET: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""

    # Email
    EMAIL_BACKEND: str = "console"
    SENDGRID_API_KEY: str = ""

    # App
    FRONTEND_URL: str = "http://localhost:3001"
    CORS_ORIGINS: list[str] = ["http://localhost:3001"]
    ENVIRONMENT: str = "development"

    # Tenancy
    MIN_TENANCY_DAYS: int = 60

    # Credits pricing (cost in credits to unlock)
    CREDIT_PRICE_UNLOCK_SUMMARY: int = 5
    CREDIT_PRICE_UNLOCK_DETAILED: int = 15
    CREDIT_PRICE_UNLOCK_FULL: int = 30
    CREDIT_PRICE_CONTACT_REQUEST: int = 25

    # Stripe top-up products (amount in cents, credits granted)
    CREDIT_TOPUP_SMALL_CENTS: int = 500
    CREDIT_TOPUP_SMALL_CREDITS: int = 20
    CREDIT_TOPUP_MEDIUM_CENTS: int = 1000
    CREDIT_TOPUP_MEDIUM_CREDITS: int = 50
    CREDIT_TOPUP_LARGE_CENTS: int = 1800
    CREDIT_TOPUP_LARGE_CREDITS: int = 100

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
