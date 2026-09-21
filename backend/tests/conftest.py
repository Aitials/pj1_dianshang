"""pytest 公共夹具。

设计原则：本目录的用例**不连接 MySQL / Redis**，可直接 `pytest` 运行。
- test_security.py、test_response.py 只测纯函数。
- test_api_contract.py 用局部构造的 FastAPI 应用 + 依赖覆盖，验证 deps.py 的鉴权与分页行为，
  刻意**不导入 app.main**——该模块在导入期会执行 Base.metadata.create_all(bind=engine)，强制连 MySQL。
"""

import pytest
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.api.deps import get_current_user, page_params, require_permission
from app.core.response import fail


class FakeUser:
    """替代 ORM 用户对象：deps.py 只用到 .id 与 .username。"""

    def __init__(self, user_id=1, username="tester"):
        self.id = user_id
        self.username = username


@pytest.fixture
def fake_user():
    return FakeUser()


@pytest.fixture
def app():
    test_app = FastAPI()

    @test_app.get("/need-login")
    def need_login(current_user=Depends(get_current_user)):
        return {"code": 0, "message": "success", "data": current_user.username}

    @test_app.get("/need-permission")
    def need_permission(current_user=Depends(require_permission("dashboard:read"))):
        return {"code": 0, "message": "success", "data": current_user.username}

    @test_app.get("/page")
    def page(params=Depends(page_params)):
        return {"code": 0, "message": "success", "data": params}

    # 与 app/main.py 保持一致：异常也走统一响应体 {code, message, data}
    @test_app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content=fail(exc.status_code, exc.detail))

    @test_app.exception_handler(RequestValidationError)
    async def validation_exc_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content=fail(422, "参数校验失败"))

    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app)