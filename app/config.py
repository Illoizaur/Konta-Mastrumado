# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./secure_auth.db")

# Тимчасова заглушка, потім зміню
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-here-please-change-it")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

CAPTCHA_ENABLED = os.getenv("CAPTCHA_ENABLED", "true").lower() == "true"

RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")

RECAPTCHA_VERIFY_URL = os.getenv(
    "RECAPTCHA_VERIFY_URL",
    "https://www.google.com/recaptcha/api/siteverify"
)
