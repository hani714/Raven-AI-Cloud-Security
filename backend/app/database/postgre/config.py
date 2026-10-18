from app.utils import settings


def get_database_url() -> str:
    url = settings.DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Ensure SQLAlchemy async engine always uses asyncpg in runtime environments.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


DATABASE_URL = get_database_url()
