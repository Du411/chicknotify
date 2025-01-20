from sqlalchemy.orm import Session
from typing import List
from app.models.jobs import Job
from app.services.scraper_service import JobDetail

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_jobs(self, jobs: List[JobDetail]) -> bool:
        new_jobs = []
        for job in jobs:
            existing_job = self.db.query(Job).filter(Job.url == job.url).first()
            if existing_job:
                continue
            new_job = Job(
                title=job.title,
                employer=job.employer,
                location=job.location,
                salary=job.salary,
                content=job.content,
                url=job.url,
                time=job.job_time,
                created_at=job.created_at,
            )
            self.db.add(new_job)
            self.db.flush()
            self.db.refresh(new_job)
            new_jobs.append(new_job)

        if new_jobs:
            self.db.commit()
            return new_jobs
        else:
            return None
