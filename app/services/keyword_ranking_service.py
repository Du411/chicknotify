from sqlalchemy.orm import Session
from sqlalchemy import func, text
from fastapi import HTTPException, status
from app.models.subscription_items import SubscriptionItem
from app.models.user_subscriptions import UserSubscription
from app.core.logger import logger
from redis import Redis
from typing import List

POPULAR_KEYWORDS_SORTED_SET = "popular_keywords_zset"
CACHE_EXPIRATION = 3600

class KeywordRankingService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis

    async def update_keyword_score(self, keyword: str):
        try:
            self.redis.zincrby(POPULAR_KEYWORDS_SORTED_SET, 1, keyword)
        except Exception as e:
            logger.error(f"Error updating keyword score: {e}")

    async def decrease_keyword_score(self, keyword: str):
        try:
            self.redis.zincrby(POPULAR_KEYWORDS_SORTED_SET, -1, keyword)
            score = self.redis.zscore(POPULAR_KEYWORDS_SORTED_SET, keyword)
            if score <= 0:
                self.redis.zrem(POPULAR_KEYWORDS_SORTED_SET, keyword)
        except Exception as e:
            logger.error(f"Error decreasing keyword score: {e}")

    async def get_popular_keywords(self, limit: int = 10) -> List[dict]:
        try:
            popular_keywords = self.redis.zrevrange(
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
                    self.redis.zadd(
                        POPULAR_KEYWORDS_SORTED_SET, 
                        {keyword: count}
                    )

                popular_keywords = self.redis.zrevrange(
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
            logger.error(f"Error getting popular keywords: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
