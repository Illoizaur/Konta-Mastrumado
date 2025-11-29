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
from .schemas import UserCreate, User as UserSchema, TokenData, Token
from .security import verify_password, create_access_token, get_token_from_cookie, verify_token
from .crud import get_user_by_email, create_user, get_user
from .config import ACCESS_TOKEN_EXPIRE_MINUTES

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
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_model=UserSchema)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач із цією електронною поштою вже існує"
        )
    
    new_user = create_user(db, user)
   
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
