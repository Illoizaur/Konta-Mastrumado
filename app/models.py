# app/models.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

from .database import Base

class User(Base):
    """
    Модель користувача для бази даних
    Ця модель в майбутньому буде розширюватись наступними завданнями:
    - Додавання полів для активації облікового запису
    - Поля для 2FA та OAuth (якщо необхідно)
    - Поля для відстеження невдалих спроб входу та логування
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
