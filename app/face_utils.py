import io
import base64
import tempfile
import os
import numpy as np
from PIL import Image
from deepface import DeepFace


def image_bytes_to_jpeg(image_bytes: bytes) -> bytes:
    """Har qanday formatdagi rasmni JPEG bytes ga o'giradi"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def base64_to_numpy(image_base64: str) -> np.ndarray:
    """Base64 string → numpy array"""
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]
    raw = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(img)


def bytes_to_numpy(image_bytes: bytes) -> np.ndarray:
    """bytes → numpy array"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(img)


def verify_face_from_bytes(
    input_base64: str,
    stored_bytes: bytes,
) -> dict:
    """
    Kamera rasmini (base64) DB'dagi rasm bytes bilan taqqoslaydi.
    Vaqtinchalik fayllarni tempfile orqali yaratadi — disk yo'li kerak emas.
    """
    try:
        input_arr = base64_to_numpy(input_base64)
        stored_arr = bytes_to_numpy(stored_bytes)

        result = DeepFace.verify(
            img1_path=input_arr,
            img2_path=stored_arr,
            model_name="Facenet512",
            detector_backend="opencv",
            enforce_detection=True,
        )
        confidence = round((1 - result["distance"]) * 100, 2)
        return {
            "verified": result["verified"],
            "confidence": confidence,
            "distance": result["distance"],
        }
    except Exception as e:
        print(f"[face_utils] verify xatosi: {e}")
        return {"verified": False, "confidence": 0.0, "distance": 1.0}


# ── Eski disk-based funksiya (backward compat, local dev uchun) ──────────────
def save_face_image(student_id: str, image_bytes: bytes, save_dir: str) -> str:
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{student_id}.jpg")
    jpeg_bytes = image_bytes_to_jpeg(image_bytes)
    with open(path, "wb") as f:
        f.write(jpeg_bytes)
    return path
