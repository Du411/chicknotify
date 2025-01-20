import urllib3
import os
import redis
import json
import re
import requests
from datetime import datetime
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
DB_SERVER = os.environ['DB_SERVER']
DB_PORT = os.environ['DB_PORT']

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

REDIS_SERVER = os.environ['REDIS_SERVER']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']


Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    employer = Column(String(255), nullable=False)
    location = Column(String(255))
    salary = Column(String(255))
    content = Column(Text)
    url = Column(String(255), unique=True)
    time = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

class JobDetail(BaseModel):
    title: str
    employer: str
    location: str
    salary: str
    content: Optional[str]
    url: str
    job_time: Optional[str]
    created_at: datetime

class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_SERVER,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
    
    def exists(self, key: str) -> bool:
        return self.redis_client.exists(key)
        
    def set(self, key: str, value: str, ex: int = None):
        return self.redis_client.set(key, value, ex=ex)
        
    def get(self, key: str) -> str:
        return self.redis_client.get(key)
        
    def publish(self, channel: str, message: str):
        return self.redis_client.publish(channel, message)

def parse_work_time(soup: BeautifulSoup) -> Optional[str]:
    work_time_section = soup.find("section", class_="job-work_time")
    if work_time_section:
        text = work_time_section.find("p", class_="text l-line-light").text.strip()
        work_date_match = re.search(r"工作日期：(\S+)(?:~(\S+))?", text)
        return work_date_match.group(1) if work_date_match else None
    return None

def get_job_details(job_url: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        response = requests.get(job_url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        job_contents = soup.find("ul", class_="content-list")
        contents_text = []
        if job_contents:
            for li in job_contents.find_all("li", class_="text l-line-light pre-dot"):
                text = li.text.strip()
                if ":" in text:
                    key, value = text.split(":", 1)
                    contents_text.append(f"{key.strip()}: {value.strip()}")
                else:
                    contents_text.append(text)
        job_content = "\n".join(contents_text)
        job_time = parse_work_time(soup)
        
        return job_content, job_time
    except Exception as e:
        print(f"Error fetching job details: {str(e)}")
        return None, None

def scrape_chickpt(limit: int = 1) -> List[JobDetail]:
    url = "https://www.chickpt.com.tw/cases"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        job_list = soup.find("ul", id="job-list", class_="job-list show")
        jobs = job_list.find_all("li")
        
        data = []
        for job in jobs[:limit]:
            job_item = job.find("div", class_="is-blk")
            job_time = job.find("div", class_="job-info-date is-flex flex-start flex-align-center")
            job_link = job.find("a", class_="job-list-item")
            
            if job_item and job_time and job_link:
                job_url = job_link['href']
                title = job_item.find("h2", class_="job-info-title").text.strip()
                employer = job_item.find("p", class_="mobile-job-company").text.strip()
                job_detail = job_item.find("p", class_="job_detail")
                salary = job_detail.find("span", class_="salary").text.strip()
                location = job_detail.find("span", class_="place").text.strip()
                
                job_content, job_time = get_job_details(job_url)
                
                data.append(JobDetail(
                    title=title,
                    employer=employer,
                    location=location,
                    salary=salary,
                    content=job_content,
                    url=job_url,
                    job_time=job_time,
                    created_at=datetime.now()
                ))
        return data
    except Exception as e:
        print(f"Error scraping chickpt: {str(e)}")
        return []

def save_jobs(db: Session, jobs: List[JobDetail]) -> bool:
    try:
        redis_client = RedisClient()
        new_jobs=[]
        for job in jobs:
            if redis_client.exists(f"job_url:{job.url}"):
                continue
            existing_job = db.query(Job).filter(Job.url == job.url).first()
            if existing_job:
                redis_client.set(f"job_url:{job.url}", "1", ex=86400)
                continue
            new_job = Job(
                title=job.title,
                employer=job.employer,
                location=job.location,
                salary=job.salary,
                content=job.content,
                url=job.url,
                time=job.job_time,
                created_at=job.created_at
            )
            db.add(new_job)
            db.flush()
            db.refresh(new_job)
            new_jobs.append(new_job)
            redis_client.set(f"job_url:{job.url}", "1", ex=86400)
        print(f"new_jobs: {new_jobs}")
        if new_jobs:
            db.commit()
            publish_new_jobs(new_jobs, redis_client)
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error saving jobs: {str(e)}")
        return False

def publish_new_jobs(jobs: List[Job], redis_client: RedisClient):
    try:
        for job in jobs:
            job_data = {
                'id': job.id,
                "title": job.title,
                "employer": job.employer,
                "location": job.location,
                "salary": job.salary,
                "content": job.content,
                "url": job.url,
                "time": job.time,
                "created_at": job.created_at.isoformat()
            }
            redis_client.publish('new_job', json.dumps(job_data))
    except Exception as e:
        print(f"Redis publish error: {str(e)}")


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def lambda_handler(event, context):
    try:
        db = SessionLocal()
        jobs = scrape_chickpt(limit=3)
        
        if not jobs:
            return {
                'statusCode': 200,
                'body': json.dumps({"status": "completed", "message": "No jobs scraped"})
            }
            
        if save_jobs(db, jobs):
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "status": "completed",
                    "message": f"Saved {len(jobs)} new jobs"
                })
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "status": "completed",
                    "message": "No new jobs found"
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        db.close()