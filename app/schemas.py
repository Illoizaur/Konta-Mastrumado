# app/schemas.py
from pydantic import BaseModel, validator, EmailStr
from typing import Optional
import re

class UserCreate(BaseModel):
    """
    Ця схема використовується як для реєстрації, так і для перевірки даних
    """
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        """
        Ця валідація передбачає подальший розвиток проєкту:
        - Вона забезпечує фундамент для інших завдань, зокрема 2FA та OAuth
        - Її використання у схемі можна легко розширити для інших типів облікових записів
        """
        if len(v) < 8:
            raise ValueError('Пароль має містити принаймні 8 символів')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль має містити хоча б одну велику літеру')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль має містити хоча б одну малу літеру')
        if not re.search(r'\d', v):
            raise ValueError('Пароль має містити хоча б одну цифру')
        if not re.search(r'[^a-zA-Z0-9]', v):
            raise ValueError('Пароль має містити хоча б один спеціальний символ')
        return v

class UserRegister(UserCreate):
    """
    Схема для реєстрації користувача.
    Наслідує email+password з UserCreate і додає поле для CAPTCHA.
    """
    captcha_token: Optional[str] = None
    
class User(BaseModel):
    """
    Схема для повернення даних про користувача
    Використовується для звітування про успішно створеного користувача
    """
    id: int
    email: EmailStr
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
