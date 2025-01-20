from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import json
from dotenv import load_dotenv
from app.services.scraper_service import scrape_chickpt
from app.repositories.job_repository import JobRepository
from app.dependencies.redis import redis_client
from app.core.logger import logger

load_dotenv()

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
DB_SERVER = os.environ['DB_SERVER']
DB_PORT = os.environ['DB_PORT']

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

def test_publish_new_jobs(jobs):
    try:
        for job in jobs:
            job_data = {
                "id": job.id,
                "title": job.title,
                "employer": job.employer,
                "location": job.location,
                "salary": job.salary,
                "content": job.content,
                "url": job.url,
                "time": job.time,
                "created_at": job.created_at.isoformat()
            }
            redis_client.publish('new_jobs', json.dumps(job_data))
            
    except Exception as e:
        logger.error(f"Redis publish error: {str(e)}")

async def main():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        jobs = await scrape_chickpt(limit=2)
        
        if not jobs:
            logger.info("No jobs found")
            return

        job_repo = JobRepository(db)
        saved_jobs = job_repo.save_jobs(jobs)
        if saved_jobs:
            logger.info(f"Successfully saved {len(jobs)} new jobs")
            test_publish_new_jobs(saved_jobs)
        else:
            logger.info("No new jobs to save")
            
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
