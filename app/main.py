from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, subscriptions, jobs, notifications
from app.dependencies.database import get_db
from app.dependencies.redis import get_redis, close_connection, subscribe
from app.services.notification_service import NotificationService
from app.core.logger import logger
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    redis = get_redis()
    notification_service = NotificationService(db, redis)
    
    task = asyncio.create_task(
        asyncio.to_thread(
            subscribe,
            'new_jobs',
            notification_service.process_job
        )
    )
    
    logger.info("Application startup complete")
    yield
    
    logger.info("Shutting down...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    logger.info("Closing resources...")
    db.close()
    close_connection()

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