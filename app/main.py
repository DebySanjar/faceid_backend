from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database import Base, engine
from app.routers import admin, students, attendance
from app.routers import courses, teachers, rooms, groups, payments

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tizim — O'quv Markazi CRM",
    description="Face ID davomat + CRM tizimi",
    version="2.0.0",
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
