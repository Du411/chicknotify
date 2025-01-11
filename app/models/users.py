from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    notification_type_id = Column(Integer, ForeignKey('notification_types.id'), nullable=False, default=1)
    discord_id = Column(String, nullable=True, default=None)
    telegram_id = Column(String, nullable=True, default=None)
    created_at = Column(DateTime, default=func.now())
    
    class Config:
        orm_mode = True