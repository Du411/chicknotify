from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, subscriptions, jobs, notifications
from app.db.base import get_db
from app.services.redis_service import RedisService
from app.services.notification_service import NotificationService
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    notification_service = NotificationService(db)
    redis_service = RedisService()
    
    task = asyncio.create_task(
        asyncio.to_thread(
            redis_service.subscribe,
            'new_jobs',
            notification_service.process_job
        )
    )
    
    print("Application startup complete")
    yield
    
    print("Shutting down...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    redis_service.close()
    db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["users"])
app.include_router(subscriptions.router, tags=["keywords"])
app.include_router(jobs.router, tags=["jobs"])
app.include_router(notifications.router, tags=["notifications"])