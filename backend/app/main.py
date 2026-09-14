from fastapi import FastAPI
from sqlalchemy import select
from app.repositories.user import get_user
from app.api.auth import router as auth_router
from app.models.user import User
from app.db.session import Base, engine,SessionLocal
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import Depends
app = FastAPI()

@app.get("/")
def shouye():
    return {"nihao !"}

app.include_router(auth_router, prefix="/api/auth")

Base.metadata.create_all(bind=engine)

@app.get("/test_db")
def test_db():
    db = SessionLocal()

    user = User(
        id=111,
        username="testuser",
        password_hash="mimatest"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {"message":"用户插入成功！",
            "user":user
            }

@app.get("/get_users")
def get_users(db: Session = Depends(get_db)):
    user = get_user(db, "testuser")

    if user is None:
        return {
            "message": "没有找到这个用户"
        }

    return {
        "username": user.username,
        "password_hash": user.password_hash
    }
@app.get("/test_password")
def test_password():
    password = "mimatest"

    password_hash = hash_password(password)

    return {
        "password": password,
        "password_hash": password_hash,
        "verify": verify_password(password, password_hash)
    }

@app.get("/test_jwt")
def test_jwt():
    token = create_access_token("testuser")
    return {
        "access_token": token
    }