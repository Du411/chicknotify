from abc import ABC, abstractmethod
from typing import List
from app.models.jobs import Job

class NotificationStrategy(ABC):
    @abstractmethod
    async def send(self, user_id: int, job: Job):
        pass