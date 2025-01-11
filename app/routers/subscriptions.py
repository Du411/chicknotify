from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.subscription_service import SubscriptionService
from app.services.keyword_ranking_service import KeywordRankingService
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, KeywordRankingResponse
from app.dependencies.auth import get_current_user
from typing import List

router = APIRouter()

def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(db)

def get_ranking_service(db: Session = Depends(get_db)) -> KeywordRankingService:
    return KeywordRankingService(db)

@router.post("/api/keywords/addKeyword", response_model=dict)
async def create_keyword_subscription(
    subscription: SubscriptionCreate,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: int = Depends(get_current_user)
):
    response = await subscription_service.create_subscription(current_user, subscription.keyword)
    return response

@router.delete("/api/keywords/{keyword_id}", response_model=dict)
async def delete_keyword_subscription(
    keyword_id: int,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: int = Depends(get_current_user)
):
    return await subscription_service.delete_subscription(current_user, keyword_id)

@router.get("/api/keywords", response_model=List[SubscriptionResponse])
async def get_keyword_subscriptions(
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: int = Depends(get_current_user)
):
    return subscription_service.get_user_subscriptions(current_user)

@router.get("/api/keywords/ranking", response_model=List[KeywordRankingResponse])
async def get_keyword_ranking(
    limit: int = 10,
    ranking_service: KeywordRankingService = Depends(get_ranking_service)
):
    return await ranking_service.get_popular_keywords(limit)