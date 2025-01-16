from app.dependencies.redis import redis_client

def test_redis_connection():
    try:
        redis_client.ping()
        print("Redis connection successful!")
    except Exception as e:
        print(f"Redis connection failed: {e}")

if __name__ == "__main__":
    test_redis_connection()