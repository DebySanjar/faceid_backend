from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/", response_model=List[schemas.GroupDetail])
def list_groups(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    groups = (
        db.query(models.Group)
        .options(
            joinedload(models.Group.course),
            joinedload(models.Group.teacher),
            joinedload(models.Group.schedules).joinedload(models.Schedule.room),
        )
        .all()
    )
    result = []
    for g in groups:
        out = schemas.GroupDetail.model_validate(g)
        out.student_count = db.query(models.Student).filter(
            models.Student.group_id == g.id,
            models.Student.is_active == True
        ).count()
        result.append(out)
    return result


@router.post("/", response_model=schemas.GroupOut)
def create_group(data: schemas.GroupCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    group = models.Group(**data.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/{group_id}", response_model=schemas.GroupDetail)
def get_group(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    group = (
        db.query(models.Group)
        .options(
            joinedload(models.Group.course),
            joinedload(models.Group.teacher),
            joinedload(models.Group.schedules).joinedload(models.Schedule.room),
        )
        .filter(models.Group.id == group_id)
        .first()
    )
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    out = schemas.GroupDetail.model_validate(group)
    out.student_count = db.query(models.Student).filter(
        models.Student.group_id == group_id,
        models.Student.is_active == True
    ).count()
    return out


@router.put("/{group_id}", response_model=schemas.GroupOut)
def update_group(group_id: int, data: schemas.GroupUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    group.is_active = False
    db.commit()
    return {"message": "Guruh o'chirildi"}


# ─── Schedule ─────────────────────────────────────────────
@router.post("/{group_id}/schedules", response_model=schemas.ScheduleOut)
def add_schedule(group_id: int, data: schemas.ScheduleCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    schedule = models.Schedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{group_id}/schedules/{schedule_id}")
def remove_schedule(group_id: int, schedule_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    schedule = db.query(models.Schedule).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.group_id == group_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Jadval topilmadi")
    db.delete(schedule)
    db.commit()
    return {"message": "Jadval o'chirildi"}
