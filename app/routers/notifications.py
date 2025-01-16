from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.database import get_db
from app.dependencies.redis import get_redis
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationHistoryResponse, NotificationTypeResponse
from app.dependencies.auth import get_current_user

router = APIRouter()

def get_notification_service(db: Session = Depends(get_db), redis = Depends(get_redis)) -> NotificationService:
    return NotificationService(db, redis)

@router.get("/api/notifications/history", response_model=List[NotificationHistoryResponse], tags=["notifications"])
async def get_user_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: int = Depends(get_current_user)
):    
    return await notification_service.get_user_notification_history(current_user)

@router.get("/api/notifications/types", response_model=List[NotificationTypeResponse], tags=["notifications"])
async def get_notification_types(
    notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.get_notification_types()