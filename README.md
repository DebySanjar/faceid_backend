# Tizim Backend — Face ID Davomat + CRM

FastAPI + PostgreSQL + DeepFace

---

## Lokal ishlatish

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
cp .env.example .env          # .env ni to'ldiring
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## Railway Deploy

### 1. Railway'da yangi project yarating
- railway.app → New Project → Empty Project

### 2. PostgreSQL qo'shing
- Add Service → Database → PostgreSQL
- Railway avtomatik `DATABASE_URL` environment variable yaratadi

### 3. Backend deploy qiling
- Add Service → GitHub Repo → tizimBackend repo tanlang
- Settings → Root Directory: `/` (agar repo root bo'lsa)

### 4. Environment variables qo'shing
Railway dashboard → Variables:
```
SECRET_KEY=uzun-random-kalit-min-32-belgili
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
`DATABASE_URL` Railway tomonidan avtomatik qo'shiladi (PostgreSQL service linked bo'lganda).

### 5. Deploy
Push qilganda avtomatik deploy bo'ladi.
`railway.toml` start command ni boshqaradi.

### 6. Birinchi admin yaratish
Deploy tugagandan so'ng Railway → service → Shell:
```bash
python -c "
from app.database import SessionLocal, Base, engine
from app.models import Admin
from app.auth import hash_password
Base.metadata.create_all(bind=engine)
db = SessionLocal()
admin = Admin(username='admin', hashed_password=hash_password('parol'))
db.add(admin); db.commit(); print('Admin yaratildi')
"
```

---

## API Endpoints

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | /admin/login | Admin login |
| POST | /admin/create | Birinchi admin (bir marta) |
| GET | /students/ | Talabalar ro'yxati |
| POST | /students/ | Talaba + yuz rasmi yuklash |
| GET | /students/{id}/face-image | Talaba rasmi JPEG |
| PUT | /students/{id}/face | Yuz rasmini yangilash |
| GET | /groups/ | Guruhlar |
| POST | /groups/ | Guruh yaratish |
| GET | /courses/ | Kurslar |
| GET | /teachers/ | O'qituvchilar |
| GET | /rooms/ | Xonalar |
| POST | /attendance/check-in | Face ID davomat |
| POST | /attendance/manual | Qo'lda davomat |
| GET | /attendance/stats/summary | Dashboard statistika |
| GET | /payments/ | To'lovlar |
| POST | /payments/ | To'lov qo'shish |

---

## Rasm saqlash

Rasmlar PostgreSQL `BYTEA` columnida saqlanadi — alohida storage server kerak emas.
Admin panel: `GET /students/{id}/face-image` orqali preview ko'rsatiladi.
