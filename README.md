# Tizim Backend

FastAPI + MySQL (PythonAnywhere free) — Face ID davomat + CRM

---

## PythonAnywhere Deploy (Free Plan)

### 1. Bash console'da repo clone qiling
```bash
git clone https://github.com/DebySanjar/faceid_backend.git ~/tizimBackend
cd ~/tizimBackend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. MySQL DB yarating
Dashboard → **Databases** tab → MySQL:
- DB nomi: `tizim_db` → to'liq: `USERNAME$tizim_db`
- Parolni eslang

### 3. `.env` fayl yarating
```bash
cp .env.example .env
nano .env
```
Quyidagilarni to'ldiring:
```
DATABASE_URL=mysql+pymysql://USERNAME:DBPASSWORD@USERNAME.mysql.pythonanywhere-services.com/USERNAME$tizim_db
SECRET_KEY=kamida-32-belgili-tasodifiy-kalit
FACE_IMAGES_DIR=/home/USERNAME/tizimBackend/face_images
```

### 4. Jadvallarni yarating
```bash
cd ~/tizimBackend
source .venv/bin/activate
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('OK')"
```

### 5. Web app sozlang
Dashboard → **Web** tab → **Add new web app**:
- Manual configuration → Python 3.11
- **Virtualenv**: `/home/USERNAME/tizimBackend/.venv`
- **WSGI file** ni oching, hamma narsani o'chirib quyidagini yozing:

```python
import sys, os
sys.path.insert(0, '/home/USERNAME/tizimBackend')
os.chdir('/home/USERNAME/tizimBackend')
from app.main import app as application
```

### 6. Reload qiling
Web tab → **Reload** tugmasi

### 7. Test qiling
```
https://USERNAME.pythonanywhere.com/docs
```

---

## API asosiy endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| GET | / | Health check |
| POST | /admin/login | Admin login |
| GET | /students/ | Talabalar |
| POST | /students/ | Talaba + rasm qo'shish |
| GET | /students/embeddings-list | Flutter uchun rasm list |
| GET | /students/{id}/face-image | Rasm preview |
| POST | /attendance/check-in-by-id | Flutter davomat |
| POST | /attendance/manual | Qo'lda davomat |
| GET | /attendance/stats/summary | Dashboard stats |
| GET | /groups/ | Guruhlar |
| GET | /courses/ | Kurslar |
| GET | /payments/ | To'lovlar |

---

## Lokal ishlatish

```bash
pip install -r requirements.txt
cp .env.example .env   # to'ldiring
uvicorn app.main:app --reload --port 8000
```
