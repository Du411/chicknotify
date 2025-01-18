from typing import List
from redis import Redis
from sqlalchemy.orm import Session
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService
from app.schemas.notification import NotificationHistoryResponse
from app.models.notifications import Notification
from app.models.jobs import Job
from app.services.notifications.email import EmailNotification
from app.services.notifications.discord import DiscordNotification
from app.services.notifications.telegram import TelegramNotification
from app.models.notification_types import NotificationType
from app.schemas.notification import NotificationTypeResponse
from app.core.logger import logger

class NotificationService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.subscription_service = SubscriptionService(db, redis)
        self.user_service = UserService(db)
        self.strategies = {
            'Email': EmailNotification(db),
            'Discord': DiscordNotification(),
            'Telegram': TelegramNotification()
        }
    
    def match_keyword(self, title: str, keyword: str) -> bool:
        return keyword.lower() in title.lower()

    async def process_job(self, job_data: dict):
        try:
            all_subscriptions = await self.subscription_service.get_all_subscriptions()
            matched_keywords = set()
            for sub in all_subscriptions:
                if self.match_keyword(job_data['title'], sub.keyword):
                    matched_keywords.add(sub.keyword)
            if not matched_keywords:
                return
            
            job = self.db.query(Job).filter(Job.url == job_data['url']).first()
            if not job:
                return

            notified_users = set()
            
            for keyword in matched_keywords:
                subscribers = await self.subscription_service.get_keyword_subscribers(keyword)
                
                for user_id in subscribers:
                    if user_id in notified_users:
                        continue
                    
                    preference = await self.user_service.get_user_notification_preferences(user_id)
                    if preference.notification_type in self.strategies:
                        await self.strategies[preference.notification_type].send(
                            user_id, 
                            job, 
                        )
                        
                        db_notification = Notification(
                            user_id=user_id,
                            job_id=job.id
                        )
                        self.db.add(db_notification)
                        self.db.commit()
                    
                    notified_users.add(user_id)
            
            logger.info(f"notified_users: {notified_users}")
        except Exception as e:
            logger.error(f"Error processing job: {e}")

    async def get_user_notification_history(self, user_id: int) -> List[NotificationHistoryResponse]:
        notifications = self.db.query(
            Notification, Job
        ).join(
            Job, Job.id == Notification.job_id
        ).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.sent_at.desc()
        ).all()
        
        notifications_list = []
        for notification, job in notifications:
            notification_record = NotificationHistoryResponse(
                id=notification.id,
                job_title=job.title,
                job_url=job.url,
                sent_at=notification.sent_at
            )
            notifications_list.append(notification_record)
        
        return notifications_list 

    async def send_notification(self, job_data: dict):

        await self.process_job(job_data) 

    async def get_notification_types(self) -> List[NotificationTypeResponse]:
        notification_types = self.db.query(NotificationType).all()
        result = []
        
        for notification_type in notification_types:
            result.append(
                NotificationTypeResponse(
                    id=notification_type.id,
                    type=notification_type.type,
                    description=notification_type.description
                )
            )
        
        return result