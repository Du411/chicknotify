from sqlalchemy import Column, Integer, ForeignKey
from app.dependencies.database import Base
class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('subscription_items.item_id'), nullable=False, index=True)
