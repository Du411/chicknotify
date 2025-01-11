from sqlalchemy.orm import Session
from sqlalchemy import func, text
from fastapi import HTTPException, status
from app.models.subscription_items import SubscriptionItem
from app.models.user_subscriptions import UserSubscription
from app.services.redis_service import RedisService
from typing import List

POPULAR_KEYWORDS_SORTED_SET = "popular_keywords_zset"
CACHE_EXPIRATION = 3600

class KeywordRankingService:
    def __init__(self, db: Session):
        self.db = db
        self.redis_service = RedisService()
    async def update_keyword_score(self, keyword: str):
        try:

            self.redis_service.redis_client.zincrby(POPULAR_KEYWORDS_SORTED_SET, 1, keyword)
        except Exception as e:
            print(f"Error updating keyword score: {e}")
    async def decrease_keyword_score(self, keyword: str):
        try:
            self.redis_service.redis_client.zincrby(POPULAR_KEYWORDS_SORTED_SET, -1, keyword)
            score = self.redis_service.redis_client.zscore(POPULAR_KEYWORDS_SORTED_SET, keyword)
            if score <= 0:
                self.redis_service.redis_client.zrem(POPULAR_KEYWORDS_SORTED_SET, keyword)
        except Exception as e:
            print(f"Error decreasing keyword score: {e}")
    async def get_popular_keywords(self, limit: int = 10) -> List[dict]:
        try:
            popular_keywords = self.redis_service.redis_client.zrevrange(
                POPULAR_KEYWORDS_SORTED_SET,
                0,
                limit-1,
                withscores=True
            )
            
            if not popular_keywords:
                keywords_data = (
                    self.db.query(
                        SubscriptionItem.keyword,
                        func.count(UserSubscription.user_id).label('subscriber_count')
                    )
                    .join(UserSubscription, UserSubscription.item_id == SubscriptionItem.item_id)
                    .group_by(SubscriptionItem.keyword)
                    .all()
                )
                
                for keyword, count in keywords_data:
                    self.redis_service.redis_client.zadd(
                        POPULAR_KEYWORDS_SORTED_SET, 
                        {keyword: count}
                    )

                popular_keywords = self.redis_service.redis_client.zrevrange(
                    POPULAR_KEYWORDS_SORTED_SET,
                    0,
                    limit-1,
                    withscores=True
                )

            result = [
                {
                    "keyword": keyword,
                    "subscriber_count": int(score)
                }
                for keyword, score in popular_keywords
            ]

            return result

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    # async def get_popular_keywords(self, limit: int = 10) -> List[dict]:
    #     try:
    #         cached_data = self.redis_service.redis_client.get(POPULAR_KEYWORDS_CACHE_KEY)
    #         print(f"cached_data: {cached_data}")
    #         if cached_data:
    #             return json.loads(cached_data)

    #         popular_keywords = (
    #             self.db.query(
    #                 SubscriptionItem.keyword,
    #                 SubscriptionItem.created_at,
    #                 func.count(UserSubscription.user_id).label('subscriber_count')
    #             )
    #             .join(UserSubscription, UserSubscription.item_id == SubscriptionItem.item_id)
    #             .group_by(SubscriptionItem.item_id, SubscriptionItem.keyword, SubscriptionItem.created_at)
    #             .order_by(text('subscriber_count DESC'))
    #             .limit(limit)
    #             .all()
    #         )

    #         result = [
    #             {
    #                 "keyword": item.keyword,
    #                 "subscriber_count": item.subscriber_count,
    #                 "created_at": item.created_at.isoformat()
    #             }
    #             for item in popular_keywords
    #         ]

    #         self.redis_service.redis_client.setex(
    #             POPULAR_KEYWORDS_CACHE_KEY,
    #             CACHE_EXPIRATION,
    #             json.dumps(result)
    #         )

    #         return result

    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=str(e)
    #         )
