# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import Response

from .database import engine, Base, get_db
from .models import User
from .schemas import UserCreate, UserRegister, User as UserSchema, TokenData, Token
from .security import (
    verify_password, 
    create_access_token, 
    get_token_from_cookie, 
    verify_token,
    verify_captcha_token,
    CaptchaServiceError
)
from .crud import get_user_by_email, create_user, get_user
from .config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    CAPTCHA_ENABLED,
    RECAPTCHA_SITE_KEY
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Auth System")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserSchema:
    token = get_token_from_cookie(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизовано: відсутній токен"
        )
    email = verify_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сесія недійсна або прострочена"
        )
    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Користувача не знайдено"
        )
    return db_user


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def read_register_form(request: Request):
    """
    Відображає форму реєстрації.
    Передаємо в шаблон інформацію про те, чи увімкнена CAPTCHA, та site key для виджету.
    """
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "captcha_enabled": CAPTCHA_ENABLED,
            "captcha_site_key": RECAPTCHA_SITE_KEY if CAPTCHA_ENABLED else None,
        }
    )


@app.post("/register", response_model=UserSchema)
async def register_user(
    request: Request,
    payload: UserRegister,
    db: Session = Depends(get_db),
):    
    if CAPTCHA_ENABLED:
        try:
            client_ip = request.client.host if request.client else None
            is_valid_captcha = await verify_captcha_token(
                captcha_token=payload.captcha_token,
                remote_ip=client_ip,
            )
        except CaptchaServiceError as exc:
            # Проблема з самим сервісом CAPTCHA (мережа, тайм-аут, 500 від Google)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервіс CAPTCHA тимчасово недоступний. Спробуйте пізніше.",
            ) from exc

        if not is_valid_captcha:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Перевірка CAPTCHA не пройдена. Підтвердіть, що ви не робот.",
            )

    db_user = get_user_by_email(db, payload.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач із цією електронною поштою вже існує"
        )

    user_data = UserCreate(email=payload.email, password=payload.password)
    new_user = create_user(db, user_data)

    return new_user
@app.get("/login", response_class=HTMLResponse)
async def read_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/token")
async def login_for_access_token(
    form_data: UserCreate,
    response: Response, 
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, form_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильна електронна пошта або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильна електронна пошта або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True для HTTPS
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
        
    return {"message": "Успішний вхід"}

@app.get("/profile", response_class=HTMLResponse)
async def read_profile(
    request: Request, 
    current_user: UserSchema = Depends(get_current_user)
):
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})
