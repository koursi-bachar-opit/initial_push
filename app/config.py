from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import os

class Settings(BaseSettings):
    """
    Centralized configuration class.
    Automatically loads values from environment variables
    (including GitHub Secrets during CI/CD runs).
    """

    model_config = ConfigDict(
        env_file=".env",               # Still allows local .env for devs
        case_sensitive=True,
        extra="ignore"
    )

    # Environment type: local / ci / prod
    ENV: str = Field(default="local")

    # Database connection (prefer GitHub secrets if defined)
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # Optional test DB for CI/CD
    TEST_DATABASE_URL: str | None = os.getenv("TEST_DATABASE_URL")

    # Auth / crypto keys
    SUPABASE_JWT_PUBLIC_KEY: str | None = os.getenv("SUPABASE_JWT_PUBLIC_KEY")
    ENCRYPTION_KEY: str | None = None

    # Database user/pass (used for local docker-compose)
    POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")


settings = Settings()


# from pydantic_settings import BaseSettings
# from pydantic import Field, ConfigDict

# class Settings(BaseSettings):
#     model_config = ConfigDict(
#         env_file=".env",
#         case_sensitive=True,
#         extra="ignore"  # Allow undeclared environment variables (e.g., POSTGRES_USER)
#     )

#     # Environment
#     ENV: str = Field(default="local")

#     # Database (single unified app DB)
#     DATABASE_URL: str = Field(
#         #default=""#
#     )

#     # Optional auth/crypto placeholders (safe for future use)
#     SUPABASE_JWT_PUBLIC_KEY: str | None = None
#     ENCRYPTION_KEY: str | None = None


# settings = Settings()