from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=List[schemas.RoomOut])
def list_rooms(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(models.Room).filter(models.Room.is_active == True).all()


@router.post("/", response_model=schemas.RoomOut)
def create_room(data: schemas.RoomCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    room = models.Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Xona topilmadi")
    room.is_active = False
    db.commit()
    return {"message": "Xona o'chirildi"}
