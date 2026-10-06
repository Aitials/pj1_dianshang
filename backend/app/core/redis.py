import os
import redis
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

# .env 已移到项目根目录（与 backend/ 同级）。这里必须用绝对路径定位，
# 不能裸用 load_dotenv()：后者依赖当前工作目录，从 backend/ 下启动就读不到。
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger( "app.redis" )
REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2
)

def get_cache(key: str):
    try:
        value = redis_client.get(key)
    except redis.exceptions.RedisError as exc:
        logger.warning("缓存读取失败，降级为回源 key=%s err=%s" , key,exc)
        return None
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.decoder.JSONDecodeError as exc:
        logger.warning("缓存内容损坏，按未命中处理 key=%s err=%s" , key,exc)

def set_cache(key: str, value, expire: int = 600):
    try:
        redis_client.set(
            key,
            json.dumps(
                value,
                ensure_ascii=False,
                default=str
            ),
            ex=expire
        )
    except redis.exceptions.RedisError as exc:
        logger.warning("缓存写入失败 key=%s err=%s", key,exc)

def delete_cache(*keys: str):
    try:
        redis_client.delete(*keys)
    except redis.exceptions.RedisError as exc:
        logger.warning("缓存删除失败 keys=%s err=%s" , keys,exc)

def delete_cache_pattern(*pattern: str):
    keys = []
    try:
        for p in pattern:
            for k in redis_client.scan_iter(match=p):
                keys.append(k)
        if keys:
            redis_client.delete(*keys)
    except redis.exceptions.RedisError as exc:
        logger.warning("缓存批量删除失败 patterns=%s err=%s" , keys,exc)