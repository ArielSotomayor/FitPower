from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    cliente = "cliente"
    entrenador = "entrenador"
    admin = "admin"


class UserStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    verification_token = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    is_email_verified = Column(Boolean, default=False)
    status = Column(Enum(UserStatus), default=UserStatus.pending)
    verification_code = Column(String(6), nullable=True)
    verification_expires = Column(DateTime, nullable=True)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())