import os
from dotenv import load_dotenv
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

result_backend = RedisAsyncResultBackend(REDIS_URL)
broker = ListQueueBroker(REDIS_URL).with_result_backend(result_backend)
