from pydantic import BaseModel
from enum import Enum
from typing import List
from datetime import datetime
    
class NotificationPreference(BaseModel):
    user_id: int
    notification_type: str
    description: str

class JobNotification(BaseModel):
    title: str
    url: str
    matched_keywords: List[str]

class NotificationHistoryResponse(BaseModel):
    id: int
    job_title: str
    job_url: str
    sent_at: datetime

    class Config:
        from_attributes = True

class NotificationTypeResponse(BaseModel):
    id: int
    type: str
    description: str | None

    class Config:
        from_attributes = True
