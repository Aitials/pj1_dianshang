from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from jose import jwt
password_hash = PasswordHash.recommended()

SECRET_KEY = "这是一个临时密钥"
ALGORITHM = "HS256"
def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)

def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )