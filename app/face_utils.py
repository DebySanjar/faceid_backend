import io
from PIL import Image


def image_bytes_to_jpeg(image_bytes: bytes) -> bytes:
    """Har qanday formatdagi rasmni JPEG bytes ga o'giradi va saqlaydi"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
