from .base import NotificationStrategy
from app.models.jobs import Job

class DiscordNotification(NotificationStrategy):
    async def send(self, user_id: int, job: Job):
       #TODO
        pass