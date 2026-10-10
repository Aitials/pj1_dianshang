import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from jose import jwt, JWTError
from dotenv import load_dotenv
from pwdlib import PasswordHash

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # 项目根目录（.env 与 backend/ 同级）
load_dotenv(BASE_DIR / ".env")

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# access token 有效期。原为 30 分钟，但前端此前没有任何过期前兆机制：
# 用户安静停留 25 分钟后，会被下一次操作直接弹回登录页，体验很差。
# 改为 8 小时覆盖一个工作日，并配合前端"临期静默续签"
# （见 frontend/src/utils/auth.js）：请求发出前若剩余不足
# ACCESS_TOKEN_RENEW_AHEAD_MINUTES 分钟，先续签再发原请求，
# 因此只要用户不是长时间完全空闲，就不会掉线。
ACCESS_TOKEN_EXPIRE_MINUTES = 8 * 60
# 前端提前续签的阈值（分钟）。后端签发不使用，仅供前端/测试引用对齐。
ACCESS_TOKEN_RENEW_AHEAD_MINUTES = 5


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")
