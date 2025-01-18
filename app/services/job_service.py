from sqlalchemy.orm import Session
from app.models.jobs import Job
from typing import List
from redis import Redis
from datetime import timedelta

class JobService:
    CACHE_KEY = "latest_ten_jobs"
    CACHE_EXPIRE = timedelta(minutes=15)

    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis

    
    def get_latest_ten_jobs(self) -> List[Job]:
        cached_jobs = self.redis.get(self.CACHE_KEY)
        if cached_jobs:
            return cached_jobs
        jobs = self.db.query(Job).order_by(Job.created_at.desc()).limit(10).all()

        return jobs