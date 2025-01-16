from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import json
from dotenv import load_dotenv
from app.services.scraper_service import scrape_chickpt
from app.repositories.job_repository import JobRepository
from app.dependencies.redis import redis

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
        print(jobs)
        for job in jobs:
            job_data = {
                "title": job.title,
                "employer": job.employer,
                "location": job.location,
                "salary": job.salary,
                "content": job.content,
                "url": job.url,
                "time": job.job_time
            }
            redis.publish('new_jobs', json.dumps(job_data))
            print(f"Published job: {job.title}")
            
    except Exception as e:
        print(f"Redis publish error: {str(e)}")

async def main():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        jobs = await scrape_chickpt(limit=2)
        
        if not jobs:
            print("No jobs found")
            return

        job_repo = JobRepository(db)
        if job_repo.save_jobs(jobs):
            print(f"Successfully saved {len(jobs)} new jobs")
            test_publish_new_jobs(jobs)
        else:
            print("No new jobs to save")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
