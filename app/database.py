from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings


def _build_url(url: str) -> str:
    """
    Turli formatlarni normalize qiladi:
      postgres://...   → postgresql://...   (Railway)
      postgresql://... → saqlanadi          (Railway paid)
      mysql://...      → mysql+pymysql://... (PythonAnywhere)
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+pymysql://", 1)
    return url


_url = _build_url(settings.DATABASE_URL)

# PythonAnywhere MySQL'da pool_size ishlamaydi (NullPool kerak)
_is_mysql = "mysql" in _url

engine = create_engine(
    _url,
    pool_pre_ping=True,
    pool_recycle=280,          # MySQL 5 daqiqalik timeout dan oldin recycle
    **({} if _is_mysql else {"pool_size": 5, "max_overflow": 10}),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
