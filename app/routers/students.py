from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin
from app.face_utils import save_face_image, read_face_image_base64, image_bytes_to_jpeg
from app.config import settings

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/embeddings-list", summary="Flutter uchun: id + base64 rasm ro'yxati")
def embeddings_list(db: Session = Depends(get_db)):
    """Flutter app shu endpoint orqali rasmlarni yuklab local embedding chiqaradi."""
    students = db.query(models.Student).filter(
        models.Student.is_active == True,
        models.Student.face_image_path.isnot(None),
    ).all()
    result = []
    for s in students:
        b64 = read_face_image_base64(s.face_image_path)
        if b64:
            result.append({
                "id": s.id,
                "full_name": s.full_name,
                "student_id": s.student_id,
                "face_image_data": b64,
            })
    return result


@router.get("/", response_model=List[schemas.StudentDetail])
def list_students(
    group_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    query = db.query(models.Student).options(joinedload(models.Student.group))
    if group_id is not None:
        query = query.filter(models.Student.group_id == group_id)
    if is_active is not None:
        query = query.filter(models.Student.is_active == is_active)
    if search:
        query = query.filter(
            models.Student.full_name.ilike(f"%{search}%") |
            models.Student.student_id.ilike(f"%{search}%") |
            models.Student.phone.ilike(f"%{search}%")
        )
    return query.order_by(models.Student.full_name).all()


@router.post("/", response_model=schemas.StudentOut)
def create_student(
    full_name: str = Form(...),
    student_id: str = Form(...),
    phone: Optional[str] = Form(None),
    parent_phone: Optional[str] = Form(None),
    birth_date: Optional[date] = Form(None),
    address: Optional[str] = Form(None),
    group_id: Optional[int] = Form(None),
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    existing = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu ID raqamli talaba allaqachon mavjud")

    image_bytes = face_image.file.read()
    face_path = save_face_image(student_id, image_bytes, settings.face_images_abs)

    student = models.Student(
        full_name=full_name,
        student_id=student_id,
        phone=phone,
        parent_phone=parent_phone,
        birth_date=birth_date,
        address=address,
        group_id=group_id,
        face_image_path=face_path,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    # face_image_data ni response ga qo'shmaslik (katta binary)
    return student
def get_student(student_db_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    student = (
        db.query(models.Student)
        .options(joinedload(models.Student.group))
        .filter(models.Student.id == student_db_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    return student


@router.put("/{student_db_id}", response_model=schemas.StudentOut)
def update_student(
    student_db_id: int,
    data: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    student = db.query(models.Student).filter(models.Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


@router.put("/{student_db_id}/face", response_model=schemas.StudentOut)
def update_face(
    student_db_id: int,
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Talaba yuz rasmini yangilash"""
    student = db.query(models.Student).filter(models.Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    image_bytes = face_image.file.read()
    student.face_image_path = save_face_image(
        student.student_id, image_bytes, settings.face_images_abs
    )
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_db_id}")
def delete_student(student_db_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    student = db.query(models.Student).filter(models.Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    student.is_active = False
    db.commit()
    return {"message": "Talaba o'chirildi"}


@router.get("/{student_db_id}/face-image")
def get_face_image(student_db_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    """Talaba yuz rasmini JPEG sifatida qaytaradi"""
    from fastapi.responses import FileResponse
    student = db.query(models.Student).filter(models.Student.id == student_db_id).first()
    if not student or not student.face_image_path:
        raise HTTPException(status_code=404, detail="Rasm topilmadi")
    import os
    if not os.path.exists(student.face_image_path):
        raise HTTPException(status_code=404, detail="Rasm faylda topilmadi")
    return FileResponse(student.face_image_path, media_type="image/jpeg")


@router.get("/{student_db_id}/attendance", response_model=List[schemas.AttendanceOut])
def student_attendance(
    student_db_id: int,
    month: Optional[str] = None,   # "2026-09"
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    query = db.query(models.Attendance).filter(models.Attendance.student_id == student_db_id)
    if month:
        year, m = month.split("-")
        query = query.filter(
            models.Attendance.date >= date(int(year), int(m), 1)
        )
    return query.order_by(models.Attendance.date.desc()).all()


@router.get("/{student_db_id}/payments", response_model=List[schemas.PaymentOut])
def student_payments(student_db_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return (
        db.query(models.Payment)
        .filter(models.Payment.student_id == student_db_id)
        .order_by(models.Payment.payment_date.desc())
        .all()
    )
