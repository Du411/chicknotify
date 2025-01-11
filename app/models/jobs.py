from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    employer = Column(String)
    location = Column(String)
    salary = Column(String)
    content = Column(String)
    url = Column(String, unique=True, index=True)
    time = Column(String)
    created_at = Column(DateTime, server_default=func.now())
