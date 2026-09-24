from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=List[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(models.Course).all()


@router.post("/", response_model=schemas.CourseOut)
def create_course(data: schemas.CourseCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    course = models.Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    return course


@router.put("/{course_id}", response_model=schemas.CourseOut)
def update_course(course_id: int, data: schemas.CourseUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    db.delete(course)
    db.commit()
    return {"message": "Kurs o'chirildi"}
