import re
import requests
from datetime import datetime
from typing import List, Tuple, Optional
from bs4 import BeautifulSoup
from pydantic import BaseModel
from app.core.logger import logger
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class JobDetail(BaseModel):
    id: Optional[int] = None
    title: str
    employer: str
    location: str
    salary: str
    content: Optional[str]
    url: str
    job_time: Optional[str]
    created_at: datetime


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
        logger.error(f"Error fetching job details: {str(e)}")
        return None, None


async def scrape_chickpt(limit: int) -> List[JobDetail]:
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
            job_time = job.find(
                "div", class_="job-info-date is-flex flex-start flex-align-center"
            )
            job_link = job.find("a", class_="job-list-item")

            if job_item and job_time and job_link:
                job_url = job_link['href']
                title = job_item.find("h2", class_="job-info-title").text.strip()
                employer = job_item.find("p", class_="mobile-job-company").text.strip()
                job_detail = job_item.find("p", class_="job_detail")
                salary = job_detail.find("span", class_="salary").text.strip()
                location = job_detail.find("span", class_="place").text.strip()

                job_content, job_time = get_job_details(job_url)

                data.append(
                    JobDetail(
                        title=title,
                        employer=employer,
                        location=location,
                        salary=salary,
                        content=job_content,
                        url=job_url,
                        job_time=job_time,
                        created_at=datetime.now(),
                    )
                )
        logger.info(f"Successfully scraped {len(data)} jobs")
        return data
    except Exception as e:
        logger.error(f"Error scraping chickpt: {str(e)}")
