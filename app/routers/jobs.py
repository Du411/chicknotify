from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.job import JobResponse
from app.services.job_service import JobService

router = APIRouter()

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)

@router.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(
    job_service: JobService = Depends(get_job_service),
    _: int = Depends(get_current_user)
):
    return job_service.get_all_jobs() 