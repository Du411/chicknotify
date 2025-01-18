from app.dependencies.redis import redis_client
from app.core.logger import logger

def test_redis_connection():
    try:
        redis_client.ping()
        logger.info("Redis connection successful!")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")

if __name__ == "__main__":
    test_redis_connection()