from pydantic import BaseModel
from datetime import datetime

class JobResponse(BaseModel):
    id: int
    title: str
    employer: str
    location: str
    salary: str
    content: str
    url: str
    time: str
    created_at: datetime

    class Config:
        from_attributes = True 