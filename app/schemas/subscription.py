from pydantic import BaseModel
from datetime import datetime
from typing import List

class SubscriptionCreate(BaseModel):
    keyword: str

class SubscriptionResponse(BaseModel):
    item_id: int
    keyword: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserSubscriptionsResponse(BaseModel):
    subscriptions: List[SubscriptionResponse] 

class SubscriptionUpdate(BaseModel):
    keyword: str

class KeywordRankingResponse(BaseModel):
    keyword: str
    subscriber_count: int

    class Config:
        from_attributes = True

