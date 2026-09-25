"""
PythonAnywhere WSGI fayli.

Deploy qilish uchun:
1. Bu faylni /var/www/USERNAME_pythonanywhere_com_wsgi.py ga ko'chiring
   YOKI Web tab → WSGI configuration file yo'lini shu faylga o'zgartiring.
2. USERNAME ni o'z username'ingiz bilan almashtiring.
"""
import sys
import os

# ── Loyiha yo'li ──────────────────────────────────────────────────────────────
PROJECT_HOME = '/home/USERNAME/tizimBackend'   # <── o'zgartiring

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# .env faylini yuklash uchun ishchi papkani o'zgartirish
os.chdir(PROJECT_HOME)

# ── App import ────────────────────────────────────────────────────────────────
from app.main import app as application  # noqa: E402
