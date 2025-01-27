import json
import asyncio
from redis import Redis, ConnectionPool
from app.core.config import settings
from app.core.logger import logger

pool = ConnectionPool(
    host=settings.REDIS_SERVER,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD.get_secret_value(),
    max_connections=settings.REDIS_POOL_SIZE,
    decode_responses=True,
)

redis_client = Redis(connection_pool=pool)

def get_redis():
    try:
        yield redis_client
    finally:
        pass

def update_latest_jobs_cache(new_job_data: dict, max_jobs: int = 10):
    try:
        cached_jobs = redis_client.get('latest_jobs')
        if cached_jobs:
            jobs_list = json.loads(cached_jobs)
        else:
            jobs_list = []
            
        jobs_list.insert(0, new_job_data)
        if len(jobs_list) > max_jobs:
            jobs_list = jobs_list[:max_jobs]
            
        redis_client.set('latest_jobs', json.dumps(jobs_list))
        
    except Exception as e:
        logger.error(f"Error updating cache: {str(e)}")

def subscribe(channel: str, message_handler):
    try:
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel)

        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    update_latest_jobs_cache(data)
                    logger.info(f"receive new job: {data['title']}")

                    asyncio.run(message_handler(data))

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

    except Exception as e:
        logger.error(f"Redis subscribe error: {str(e)}")

def close_connection():
    pool.close()
