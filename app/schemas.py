from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, time
from app.models import PaymentStatus, DayOfWeek


# ─── Admin ────────────────────────────────────────────────
class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# ─── Course ───────────────────────────────────────────────
class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration_months: int = 3
    monthly_fee: float = 0.0

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None
    monthly_fee: Optional[float] = None
    is_active: Optional[bool] = None

class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    duration_months: int
    monthly_fee: float
    is_active: bool
    class Config:
        from_attributes = True


# ─── Teacher ──────────────────────────────────────────────
class TeacherCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    subject: Optional[str] = None

class TeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    is_active: Optional[bool] = None

class TeacherOut(BaseModel):
    id: int
    full_name: str
    phone: Optional[str]
    subject: Optional[str]
    is_active: bool
    class Config:
        from_attributes = True


# ─── Room ─────────────────────────────────────────────────
class RoomCreate(BaseModel):
    name: str
    capacity: int = 20

class RoomOut(BaseModel):
    id: int
    name: str
    capacity: int
    is_active: bool
    class Config:
        from_attributes = True


# ─── Schedule ─────────────────────────────────────────────
class ScheduleCreate(BaseModel):
    group_id: int
    room_id: Optional[int] = None
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

class ScheduleOut(BaseModel):
    id: int
    group_id: int
    room_id: Optional[int]
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    room: Optional[RoomOut]
    class Config:
        from_attributes = True


# ─── Group ────────────────────────────────────────────────
class GroupCreate(BaseModel):
    name: str
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_students: int = 20

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None

class GroupOut(BaseModel):
    id: int
    name: str
    course_id: Optional[int]
    teacher_id: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]
    max_students: int
    is_active: bool
    class Config:
        from_attributes = True

class GroupDetail(GroupOut):
    course: Optional[CourseOut]
    teacher: Optional[TeacherOut]
    schedules: List[ScheduleOut] = []
    student_count: Optional[int] = None


# ─── Student ──────────────────────────────────────────────
class StudentCreate(BaseModel):
    full_name: str
    student_id: str
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    group_id: Optional[int] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    group_id: Optional[int] = None
    is_active: Optional[bool] = None

class StudentOut(BaseModel):
    id: int
    full_name: str
    student_id: str
    phone: Optional[str]
    parent_phone: Optional[str]
    birth_date: Optional[date]
    address: Optional[str]
    group_id: Optional[int]
    is_active: bool
    has_face: bool = False        # rasm bor/yo'qligini bildiradi
    created_at: datetime
    class Config:
        from_attributes = True

class StudentDetail(StudentOut):
    group: Optional[GroupOut]


# ─── Attendance ───────────────────────────────────────────
class AttendanceOut(BaseModel):
    id: int
    student_id: int
    date: date
    check_in_time: datetime
    confidence: Optional[float]
    marked_by_admin: bool
    student: Optional[StudentOut]
    class Config:
        from_attributes = True

class FaceCheckIn(BaseModel):
    """Face ID orqali davomat (eski)"""
    image_base64: str

class AttendanceManual(BaseModel):
    """Admin qo'lda davomat belgilash"""
    student_id: int
    date: date

class CheckInById(BaseModel):
    """Flutter ML Kit — faqat student id va confidence yuboriladi"""
    student_db_id: int
    confidence: float


# ─── Payment ──────────────────────────────────────────────
class PaymentCreate(BaseModel):
    student_id: int
    amount: float
    payment_date: date
    month: str        # "2026-09"
    status: PaymentStatus = PaymentStatus.paid
    note: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    student_id: int
    amount: float
    payment_date: date
    month: str
    status: PaymentStatus
    note: Optional[str]
    created_at: datetime
    student: Optional[StudentOut]
    class Config:
        from_attributes = True


# ─── Dashboard ────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_students: int
    active_students: int
    total_groups: int
    active_groups: int
    total_teachers: int
    present_today: int
    absent_today: int
    total_income_this_month: float
