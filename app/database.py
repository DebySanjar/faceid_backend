from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Railway postgres:// → postgresql:// fix
url = settings.DATABASE_URL
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    url,
    pool_pre_ping=True,       # ulanish uzilsa avtomatik qayta ulanadi
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
