import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # PythonAnywhere'da absolute yo'l ishlatiladi
    # Masalan: /home/yourusername/tizimBackend/face_images
    FACE_IMAGES_DIR: str = "face_images"

    @property
    def face_images_abs(self) -> str:
        """Absolute yo'l qaytaradi"""
        if os.path.isabs(self.FACE_IMAGES_DIR):
            return self.FACE_IMAGES_DIR
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.FACE_IMAGES_DIR)

    class Config:
        env_file = ".env"

settings = Settings()
