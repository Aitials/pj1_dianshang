from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.session import get_db
from app.core.response import ok, ok_page
from app.schemas.response import ApiResponse, PageData
from app.schemas.logistics import LogisticsOverviewResponse ,logistics_geoResponse ,logistics_ratingResponse
from app.repositories.logistics import get_logistics_overview ,get_logistics_geo ,get_delay_rating

router = APIRouter()


@router.get("/logistics/overview" ,response_model=ApiResponse[LogisticsOverviewResponse],dependencies=[Depends(require_permission("logistics:read"))])
def logistics_overview(db: Session = Depends(get_db)):
    return ok(get_logistics_overview(db))

@router.get('/logistics/geo' , response_model=ApiResponse[logistics_geoResponse] ,dependencies=[Depends(require_permission("logistics:read"))])
def logistics_geo(db: Session = Depends(get_db)):
    geo = get_logistics_geo(db)
    return ok(geo)

@router.get('/logistics/delay-rating' ,response_model=ApiResponse[logistics_ratingResponse] , dependencies=[Depends(require_permission("logistics:read"))])
def logistics_delay(db: Session = Depends(get_db)):
    delay = get_delay_rating(db)
    return ok(delay)