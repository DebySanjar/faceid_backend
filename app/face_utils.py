import io
import os
import base64
from PIL import Image


def image_bytes_to_jpeg(image_bytes: bytes) -> bytes:
    """Har qanday formatdagi rasmni JPEG bytes ga o'giradi"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def save_face_image(student_id: str, image_bytes: bytes, save_dir: str) -> str:
    """Rasmni disk'ga saqlaydi, yo'lini qaytaradi"""
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{student_id}.jpg")
    jpeg = image_bytes_to_jpeg(image_bytes)
    with open(path, "wb") as f:
        f.write(jpeg)
    return path


def read_face_image_base64(image_path: str) -> str | None:
    """Diskdan rasmni o'qib base64 qaytaradi (Flutter uchun)"""
    if not image_path or not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()
