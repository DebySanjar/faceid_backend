from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import verify_password, hash_password, create_access_token, get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=schemas.Token)
def admin_login(data: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == data.username).first()
    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login yoki parol noto'g'ri")
    token = create_access_token({"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/create", summary="Birinchi admin yaratish (setup uchun)")
def create_admin(data: schemas.AdminLogin, db: Session = Depends(get_db)):
    existing = db.query(models.Admin).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin allaqachon mavjud")
    admin = models.Admin(username=data.username, hashed_password=hash_password(data.password))
    db.add(admin)
    db.commit()
    return {"message": "Admin yaratildi"}


@router.get("/me")
def get_me(admin=Depends(get_current_admin)):
    return {"username": admin.username, "id": admin.id}
