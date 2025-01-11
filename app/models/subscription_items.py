from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class SubscriptionItem(Base):
    __tablename__ = "subscription_items"

    item_id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True, unique=True)
    created_at = Column(DateTime, server_default=func.now())
