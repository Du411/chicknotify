import redis
from app.services.redis_service import RedisService

def test_redis_connection():
    try:
        r= RedisService()
        redis_client = r.redis_client
        response = redis_client.ping()
        if response:
            print("connect success !")
    except Exception as e:
        print(f"connect fail: {e}")

if __name__ == "__main__":
    test_redis_connection()