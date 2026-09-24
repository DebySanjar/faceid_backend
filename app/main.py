from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import Base, engine, SessionLocal
from app.routers import admin, students, attendance
from app.routers import courses, teachers, rooms, groups, payments


def _create_default_admin():
    """Agar hech qanday admin yo'q bo'lsa, default admin yaratadi."""
    from app.models import Admin
    from app.auth import hash_password
    db = SessionLocal()
    try:
        if not db.query(Admin).first():
            db.add(Admin(
                username="admin",
                hashed_password=hash_password("parol"),
            ))
            db.commit()
            print("[startup] Default admin yaratildi → login: admin / parol: parol")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _create_default_admin()
    yield


app = FastAPI(
    title="Tizim — O'quv Markazi CRM",
    description="Face ID davomat + CRM tizimi",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(courses.router)
app.include_router(teachers.router)
app.include_router(rooms.router)
app.include_router(groups.router)
app.include_router(students.router)
app.include_router(payments.router)
app.include_router(attendance.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Tizim API v2 ishlayapti", "docs": "/docs"}
