from fastapi import FastAPI ,Request ,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.response import fail,ok
from app.api.auth import router as auth_router
from app.api.products import router as product_router
from app.api.seller import router as seller_router
from app.db.session import Base, engine
from app.api.customer import router as customer_router
from app.api.order import router as order_router
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.operation_log import OperationLog
from app.api.order_reviews import router as reviews_router
from app.api.order_items import router as items_router
from app.api.order_payments import router as payments_router
from app.api.translation import router as tran_router
from app.api.geolocation import router as geolocation_router
from app.api.dashboard import router as dashboard_router
from app.api.inventory import router as inventory_router
from app.api.logistics import router as logistics_router
from app.api.user import router as user_router
from app.api.log import router as log_router
app = FastAPI()


@app.get("/healthy")
def health_check():
    return ok(message="ok")


app.include_router(auth_router, prefix="/api/auth")
app.include_router(seller_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(customer_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(items_router, prefix="/api")
app.include_router(tran_router, prefix="/api")
app.include_router(geolocation_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api/dashboard")
app.include_router(inventory_router, prefix="/api")
app.include_router(logistics_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(log_router, prefix="/api")

@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,
                        content=fail(exc.status_code, exc.detail))

@app.exception_handler(RequestValidationError)
async def validation_exc_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=fail(422, "参数校验失败"))

Base.metadata.create_all(bind=engine)
