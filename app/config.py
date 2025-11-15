from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """
    Fully environment-driven settings.
    Works for:
    - Local `.env`
    - Docker with `env_file` or environment:
    - GitHub Secrets (CI)
    - Render.com environment variables
    - Alembic migrations
    """

    # Let Pydantic handle environment variable loading.
    model_config = ConfigDict(
        env_file=".env",        # works for local dev
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    # Environment name (optional)
    ENV: str = Field(default="local")

    # Database URLs
    # Do NOT use os.getenv() — Pydantic handles it correctly across environments.
    DATABASE_URL: str = Field(..., description="Main database URL")
    TEST_DATABASE_URL: str | None = Field(default=None)

    # Supabase Auth
    SUPABASE_URL: str = Field(...)
    SUPABASE_ANON_KEY: str = Field(...)
    SUPABASE_JWT_SECRET: str = Field(...)

    # Optional: useful for Docker-based PG setups
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None


# Singleton for import
settings = Settings()

# from pydantic_settings import BaseSettings
# from pydantic import Field, ConfigDict
# import os

# class Settings(BaseSettings):
#     """
#     Centralized configuration class.
#     Automatically loads values from environment variables
#     (including GitHub Secrets during CI/CD runs).
#     """

#     model_config = ConfigDict(
#         env_file=".env",               # Still allows local .env for devs
#         case_sensitive=True,
#         extra="ignore"
#     )

#     # Environment type: local / ci / prod
#     ENV: str = Field(default="local")

#     # Database connection (prefer GitHub secrets if defined)
#     DATABASE_URL: str | None = os.getenv("DATABASE_URL")

#     # Optional test DB for CI/CD
#     TEST_DATABASE_URL: str | None = os.getenv("TEST_DATABASE_URL")

#     # # Auth / crypto keys
#     # SUPABASE_JWT_PUBLIC_KEY: str | None = os.getenv("SUPABASE_JWT_PUBLIC_KEY")
#     # ENCRYPTION_KEY: str | None = None

#     #####################
#     SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
#     SUPABASE_ANON_KEY: str | None = os.getenv("SUPABASE_ANON_KEY")
#     SUPABASE_JWT_SECRET: str | None = os.getenv("SUPABASE_JWT_SECRET")
#     #####################

#     # Database user/pass (used for local docker-compose)
#     POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")
#     POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
#     POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")


# settings = Settings()