from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.subscription_items import SubscriptionItem
from app.models.user_subscriptions import UserSubscription
from typing import List
from app.services.keyword_ranking_service import KeywordRankingService

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.ranking_service = KeywordRankingService(db)

    async def create_subscription(self, user_id: int, keyword: str):
        try:
            lowercased_keyword = keyword.lower()
            
            subscription_item = self.db.query(SubscriptionItem).filter(
                SubscriptionItem.keyword == lowercased_keyword
            ).first()
            
            if not subscription_item:
                subscription_item = SubscriptionItem(keyword=lowercased_keyword)
                self.db.add(subscription_item)
                self.db.commit()
                self.db.refresh(subscription_item)
            
            existing_subscription = self.db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.item_id == subscription_item.item_id
            ).first()
            
            if existing_subscription:
                return {"message": "Already subscribed to this keyword"}
            
            user_subscription = UserSubscription(
                user_id=user_id,
                item_id=subscription_item.item_id
            )
            self.db.add(user_subscription)
            self.db.commit()
            await self.ranking_service.update_keyword_score(lowercased_keyword)
            return {"message": "Subscription created successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_user_subscriptions(self, user_id: int):
        subscriptions = self.db.query(SubscriptionItem).join(
            UserSubscription, UserSubscription.item_id == SubscriptionItem.item_id).filter(
            UserSubscription.user_id == user_id
        ).all()

        return subscriptions

    async def delete_subscription(self, user_id: int, keyword_id: int) -> dict:
        try:
            subscription = self.db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.item_id == keyword_id
            ).first()
            
            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subscription not found"
                )

            keyword = self.db.query(SubscriptionItem.keyword).filter(
                SubscriptionItem.item_id == keyword_id
            ).scalar()
            
            self.db.delete(subscription)
            self.db.commit()

            if keyword:
                await self.ranking_service.decrease_keyword_score(keyword)
            
            return {"message": "Subscription deleted successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_all_subscriptions(self):
        try:
            subscriptions = self.db.query(SubscriptionItem).all()
            return subscriptions
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_keyword_subscribers(self, keyword: str) -> List[int]:
        try:
            subscribers = (
                self.db.query(UserSubscription.user_id)
                .join(SubscriptionItem, UserSubscription.item_id == SubscriptionItem.item_id)
                .filter(SubscriptionItem.keyword == keyword)
                .all()
            )
            return [sub[0] for sub in subscribers]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
