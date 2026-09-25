from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Float, Text, Enum, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    paid = "paid"
    unpaid = "unpaid"
    partial = "partial"


class DayOfWeek(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Course(Base):
    """Fan / Kurs — masalan: Matematika, Ingliz tili"""
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_months = Column(Integer, default=3)      # kurs davomiyligi (oy)
    monthly_fee = Column(Float, default=0.0)          # oylik to'lov (so'm)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", back_populates="course")


class Teacher(Base):
    """O'qituvchi"""
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    subject = Column(String(200), nullable=True)      # mutaxassisligi
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", back_populates="teacher")


class Room(Base):
    """Xona / Auditoriya"""
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)        # masalan: 101-xona
    capacity = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)

    schedules = relationship("Schedule", back_populates="room")


class Group(Base):
    """Guruh — kurs + o'qituvchi + talabalar"""
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    max_students = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="groups")
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("Student", back_populates="group")
    schedules = relationship("Schedule", back_populates="group")


class Schedule(Base):
    """Dars jadvali — guruh qaysi kunlari, qaysi vaqtda, qaysi xonada"""
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    group = relationship("Group", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")


class Student(Base):
    """Talaba"""
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    student_id = Column(String(50), unique=True, nullable=False)  # talaba ID raqami
    phone = Column(String(20), nullable=True)
    parent_phone = Column(String(20), nullable=True)              # ota-ona telefoni
    birth_date = Column(Date, nullable=True)
    address = Column(String(300), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    face_image_path = Column(String(500), nullable=True)   # disk'dagi yo'l
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")
    payments = relationship("Payment", back_populates="student")


class Attendance(Base):
    """Davomat"""
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in_time = Column(DateTime(timezone=True), server_default=func.now())
    confidence = Column(Float, nullable=True)
    marked_by_admin = Column(Boolean, default=False)  # admin qo'lda belgilaganmi

    student = relationship("Student", back_populates="attendances")


class Payment(Base):
    """To'lov"""
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    month = Column(String(7), nullable=False)          # "2026-09" formatida
    status = Column(Enum(PaymentStatus), default=PaymentStatus.paid)
    note = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="payments")
