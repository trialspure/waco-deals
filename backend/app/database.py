import ssl
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings


def _fix_db_url(url: str) -> tuple[str, dict]:
    """
    Returns (fixed_url, connect_args) for pg8000.
    - Converts postgresql:// -> postgresql+pg8000://
    - Strips ?sslmode= from the URL (pg8000 uses ssl_context instead)
    - Returns an SSL context in connect_args when SSL is required
    """
    needs_ssl = "sslmode=require" in url or "sslmode=verify" in url

    # Strip sslmode from query string
    if "sslmode" in url:
        parsed = urlparse(url)
        params = {k: v[0] for k, v in parse_qs(parsed.query).items() if k != "sslmode"}
        parsed = parsed._replace(query=urlencode(params))
        url = urlunparse(parsed)

    # Fix driver prefix
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("://", "+pg8000://", 1)

    connect_args = {}
    if needs_ssl:
        ctx = ssl.create_default_context()
        connect_args["ssl_context"] = ctx

    return url, connect_args


_db_url, _connect_args = _fix_db_url(settings.database_url)
engine = create_engine(
    _db_url,
    connect_args=_connect_args,
    pool_pre_ping=True,   # test connection before use, reconnect if dead
    pool_recycle=300,     # recycle connections every 5 minutes
    pool_size=5,
    max_overflow=2,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
