from fastapi import APIRouter, Depends ,Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.response import ok
from app.schemas.response import ApiResponse
from app.schemas.operation_log import OperationLogListResponse
from app.repositories.operation_log import get_logs
from app.api.deps import require_permission

router = APIRouter()


@router.get('/logs', response_model=ApiResponse[OperationLogListResponse], dependencies=[Depends(require_permission("user:read"))])
def list_logs(page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100), db: Session = Depends(get_db)):
    result = get_logs(db, page, page_size)
    return ok(result)
