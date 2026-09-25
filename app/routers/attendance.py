from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin
from app.face_utils import verify_face_from_bytes

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in", summary="Face ID orqali davomat (Flutter app)")
def face_check_in(data: schemas.FaceCheckIn, db: Session = Depends(get_db)):
    students = db.query(models.Student).filter(
        models.Student.face_image_data.isnot(None),
        models.Student.is_active == True,
    ).all()

    if not students:
        raise HTTPException(status_code=404, detail="Ro'yxatga olingan talabalar topilmadi")

    best_match = None
    best_confidence = 0.0

    for student in students:
        result = verify_face_from_bytes(data.image_base64, student.face_image_data)
        if result["verified"] and result["confidence"] > best_confidence:
            best_confidence = result["confidence"]
            best_match = student

    if not best_match:
        raise HTTPException(status_code=401, detail="Yuz aniqlanmadi yoki talaba topilmadi")

    today = date.today()
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == best_match.id,
        models.Attendance.date == today,
    ).first()

    if existing:
        return {
            "already_marked": True,
            "message": "Davomat allaqachon belgilangan",
            "student_name": best_match.full_name,
            "student_id": best_match.student_id,
            "confidence": best_confidence,
        }

    attendance = models.Attendance(
        student_id=best_match.id,
        date=today,
        confidence=best_confidence,
        marked_by_admin=False,
    )
    db.add(attendance)
    db.commit()

    return {
        "already_marked": False,
        "message": "Davomat muvaffaqiyatli belgilandi",
        "student_name": best_match.full_name,
        "student_id": best_match.student_id,
        "confidence": best_confidence,
    }


@router.post("/check-in-by-id", summary="Flutter ML Kit — student id orqali davomat")
def check_in_by_id(data: schemas.CheckInById, db: Session = Depends(get_db)):
    """
    Flutter ML Kit yuz aniqladi → faqat student_db_id va confidence yuboradi.
    Server faqat DB operatsiyasi qiladi.
    """
    student = db.query(models.Student).filter(
        models.Student.id == data.student_db_id,
        models.Student.is_active == True,
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")

    today = date.today()
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == student.id,
        models.Attendance.date == today,
    ).first()

    if existing:
        return {
            "already_marked": True,
            "message": "Davomat allaqachon belgilangan",
            "student_name": student.full_name,
            "student_id": student.student_id,
            "confidence": data.confidence,
        }

    attendance = models.Attendance(
        student_id=student.id,
        date=today,
        confidence=data.confidence,
        marked_by_admin=False,
    )
    db.add(attendance)
    db.commit()

    return {
        "already_marked": False,
        "message": "Davomat muvaffaqiyatli belgilandi",
        "student_name": student.full_name,
        "student_id": student.student_id,
        "confidence": data.confidence,
    }



def manual_check_in(data: schemas.AttendanceManual, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    student = db.query(models.Student).filter(models.Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")

    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == data.student_id,
        models.Attendance.date == data.date,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu talaba uchun shu kunda davomat allaqachon bor")

    attendance = models.Attendance(
        student_id=data.student_id,
        date=data.date,
        marked_by_admin=True,
    )
    db.add(attendance)
    db.commit()
    return {"message": f"{student.full_name} uchun davomat belgilandi"}


@router.delete("/{attendance_id}", summary="Davomatni bekor qilish")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    att = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Davomat topilmadi")
    db.delete(att)
    db.commit()
    return {"message": "Davomat bekor qilindi"}


@router.get("/today", response_model=List[schemas.AttendanceOut])
def get_today(group_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    today = date.today()
    query = (
        db.query(models.Attendance)
        .options(joinedload(models.Attendance.student))
        .filter(models.Attendance.date == today)
    )
    if group_id:
        query = query.join(models.Student).filter(models.Student.group_id == group_id)
    return query.all()


@router.get("/", response_model=List[schemas.AttendanceOut])
def get_attendance(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    group_id: Optional[int] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    query = db.query(models.Attendance).options(joinedload(models.Attendance.student))
    if date_from:
        query = query.filter(models.Attendance.date >= date_from)
    if date_to:
        query = query.filter(models.Attendance.date <= date_to)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    if group_id:
        query = query.join(models.Student).filter(models.Student.group_id == group_id)
    return query.order_by(models.Attendance.check_in_time.desc()).all()


@router.get("/stats/summary", response_model=schemas.DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    from datetime import datetime
    today = date.today()
    current_month = today.strftime("%Y-%m")

    total_students = db.query(models.Student).count()
    active_students = db.query(models.Student).filter(models.Student.is_active == True).count()
    total_groups = db.query(models.Group).count()
    active_groups = db.query(models.Group).filter(models.Group.is_active == True).count()
    total_teachers = db.query(models.Teacher).filter(models.Teacher.is_active == True).count()
    present_today = db.query(models.Attendance).filter(models.Attendance.date == today).count()

    monthly_income = db.query(models.Payment).filter(models.Payment.month == current_month).all()
    total_income = sum(p.amount for p in monthly_income)

    return schemas.DashboardStats(
        total_students=total_students,
        active_students=active_students,
        total_groups=total_groups,
        active_groups=active_groups,
        total_teachers=total_teachers,
        present_today=present_today,
        absent_today=active_students - present_today,
        total_income_this_month=total_income,
    )
