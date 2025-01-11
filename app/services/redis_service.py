import json
import asyncio
from redis import Redis
from app.core.config import settings


class RedisService:
    def __init__(self):
        self.redis_client = None
        self.connect()

    def connect(self):
        if self.redis_client:
            self.close()
        
        self.redis_client = Redis(
            host=settings.REDIS_SERVER,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD.get_secret_value(),
            decode_responses=True
        )

    def subscribe(self, channel: str, message_handler):
        try:
            if not self.redis_client:
                self.connect()
                
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(channel)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        print(f"receive new job: {data['title']}")

                        async def run_handler():
                            await message_handler(data)
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(run_handler())
                        finally:
                            loop.close()
                            
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        
        except Exception as e:
            print(f"Redis subscribe error: {str(e)}")
            self.connect()

    def close(self):
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
