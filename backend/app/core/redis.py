import os
import redis
import json
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)

def get_cache(key: str):
    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def set_cache(key: str, value, expire: int = 600):
    redis_client.set(
        key,
        json.dumps(
            value,
            ensure_ascii=False,
            default=str
        ),
        ex=expire
    )

def delete_cache(*keys: str):
    redis_client.delete(*keys)

def delete_cache_pattern(*pattern: str):
    keys = []
    for p in pattern:
        for k in redis_client.scan_iter(match=p):
            keys.append(k)
    if keys:
        redis_client.delete(*keys)