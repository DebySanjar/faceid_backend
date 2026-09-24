from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/", response_model=List[schemas.TeacherOut])
def list_teachers(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(models.Teacher).filter(models.Teacher.is_active == True).all()


@router.post("/", response_model=schemas.TeacherOut)
def create_teacher(data: schemas.TeacherCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    teacher = models.Teacher(**data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.get("/{teacher_id}", response_model=schemas.TeacherOut)
def get_teacher(teacher_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    return teacher


@router.put("/{teacher_id}", response_model=schemas.TeacherOut)
def update_teacher(teacher_id: int, data: schemas.TeacherUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    teacher.is_active = False
    db.commit()
    return {"message": "O'qituvchi o'chirildi"}
