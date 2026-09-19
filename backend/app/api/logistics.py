from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.session import get_db
from app.core.response import ok, ok_page
from app.schemas.response import ApiResponse, PageData
from app.schemas.logistics import LogisticsOverviewResponse
from app.repositories.logistics import get_logistics_overview

router = APIRouter()


@router.get("/logistics/overview" ,response_model=ApiResponse[LogisticsOverviewResponse],dependencies=[Depends(require_permission("logistics:read"))])
def logistics_overview(db: Session = Depends(get_db)):
    return ok(get_logistics_overview(db))
