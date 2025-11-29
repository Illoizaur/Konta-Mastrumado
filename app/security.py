# app/security.py

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Request, HTTPException, status
from .config import SECRET_KEY, ALGORITHM, CAPTCHA_ENABLED, RECAPTCHA_SECRET_KEY, RECAPTCHA_VERIFY_URL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_from_cookie(request:Request) -> str | None:
    return request.cookies.get("access_token")

def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

class CaptchaServiceError(Exception):
    pass

async def verify_captcha_token(
    captcha_token: Optional[str],
    remote_ip: Optional[str] = None,
) -> bool:
    """
    Перевіряє валідність CAPTCHA токена через Google reCAPTCHA v2 API.

    :param captcha_token: Токен, отриманий на фронтенді після проходження CAPTCHA
    :param remote_ip: (необов'язково) IP-адреса клієнта
    :return: True, якщо CAPTCHA пройдена успішно, False — якщо ні
    :raises CaptchaServiceError: якщо є проблеми з доступом до сервісу CAPTCHA
    """
    if not CAPTCHA_ENABLED:
        return True
 
    if not captcha_token:
        return False

    data = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": captcha_token,
    }
    if remote_ip:
        data["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(RECAPTCHA_VERIFY_URL, data=data)
    except httpx.RequestError as exc:
        raise CaptchaServiceError(
            f"Не вдалося з'єднатися з сервісом CAPTCHA: {exc}"
        ) from exc

    if resp.status_code != 200:
        raise CaptchaServiceError(
            f"Сервіс CAPTCHA повернув неочікуваний статус: {resp.status_code}"
        )

    try:
        result = resp.json()
    except ValueError as exc:
        raise CaptchaServiceError("Сервіс CAPTCHA повернув невалідну JSON-відповідь") from exc

    success = result.get("success", False)

    return bool(success)
