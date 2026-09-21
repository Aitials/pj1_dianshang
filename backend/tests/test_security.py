"""core/security.py：密码哈希与 JWT 签发/校验。不依赖任何外部服务。"""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

PASSWORD = "P@ssw0rd-测试"


def test_hash_password_is_not_plaintext():
    hashed = hash_password(PASSWORD)
    assert hashed != PASSWORD
    assert PASSWORD not in hashed


def test_hash_password_is_salted():
    """Argon2 每次加盐，同一密码两次哈希结果必须不同。"""
    assert hash_password(PASSWORD) != hash_password(PASSWORD)


def test_verify_password_accepts_correct_password():
    assert verify_password(PASSWORD, hash_password(PASSWORD)) is True


def test_verify_password_rejects_wrong_password():
    assert verify_password("wrong-password", hash_password(PASSWORD)) is False


def test_token_roundtrip_returns_username():
    username = "admin"
    assert decode_access_token(create_access_token(username)) == username


def test_token_uses_hs256_algorithm():
    header = jwt.get_unverified_header(create_access_token("admin"))
    assert header["alg"] == ALGORITHM == "HS256"


def test_token_expires_in_30_minutes():
    payload = jwt.decode(create_access_token("admin"), SECRET_KEY, algorithms=[ALGORITHM])
    remaining = datetime.fromtimestamp(payload["exp"], tz=timezone.utc) - datetime.now(timezone.utc)
    # 编码耗时忽略不计，给 1 分钟余量
    assert timedelta(minutes=29) < remaining <= timedelta(minutes=30)


def test_decode_rejects_tampered_token():
    token = create_access_token("admin")
    with pytest.raises(Exception):
        decode_access_token(token + "x")


def test_decode_rejects_token_signed_with_other_key():
    forged = jwt.encode({"sub": "admin"}, "not-the-real-secret", algorithm=ALGORITHM)
    with pytest.raises(Exception):
        decode_access_token(forged)


def test_decode_rejects_expired_token():
    expired = jwt.encode(
        {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(Exception):
        decode_access_token(expired)