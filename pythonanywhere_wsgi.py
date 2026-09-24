"""
PythonAnywhere WSGI config fayli.
PythonAnywhere dashboard'da Web tab → WSGI configuration file ga shu faylni ko'rsating.
Yoki shu faylni /var/www/yourusername_pythonanywhere_com_wsgi.py ga ko'chiring.
"""
import sys
import os

# Loyiha yo'lini Python path'ga qo'shish
project_home = '/home/yourusername/tizimBackend'  # <-- o'zgartiring
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# .env faylini yuklash
os.chdir(project_home)

from app.main import app as application  # noqa
