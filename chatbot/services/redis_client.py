import redis
import os

# Use env vars or defaults
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


def get_last_intent(user_id: str):
    return redis_client.get(f"chatbot:last_intent:{user_id}")


def set_last_intent(user_id: str, tag: str):
    redis_client.set(f"chatbot:last_intent:{user_id}", tag, ex=300)  # expire in 5 min


def clear_last_intent(user_id: str):
    redis_client.delete(f"chatbot:last_intent:{user_id}")