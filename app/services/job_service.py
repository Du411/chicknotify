from sqlalchemy.orm import Session
from app.models.jobs import Job
from typing import List

class JobService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_jobs(self) -> List[Job]:
        jobs = self.db.query(Job).order_by(Job.created_at.desc()).all() 
        return jobs