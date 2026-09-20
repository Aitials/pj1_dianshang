from fastapi import APIRouter ,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.dashboard import count_orders, avg_reviews, count_customers,total_sales,avg_order_value,sales_trend,get_category_ranking,get_seller_ranking,get_sned_time,get_overview ,get_productsranking ,get_alerts
from app.schemas.dashboard import DashboardOverviewResponse ,Productrankresponse ,CategoryRankingResponse ,Seller_rankresponse ,Send_time_rateresponse ,AlertResponse
from app.api.deps import require_permission
from app.core.response import ok
from app.schemas.response import ApiResponse
router = APIRouter()

@router.get("/overview" , response_model=ApiResponse[DashboardOverviewResponse] ,dependencies=[Depends(require_permission("dashboard:read"))])
def overview(db: Session = Depends(get_db)):
    result = get_overview(db)
    return ok(result)

@router.get("/trend" ,dependencies=[Depends(require_permission("dashboard:read"))])
def trend(db: Session = Depends(get_db)):
    return {
        "trend" : sales_trend(db),
    }

@router.get("/category-ranking", response_model= CategoryRankingResponse ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_category_ranking(db : Session = Depends(get_db) , top : int = 10):
    return {
        "category_ranking" : get_category_ranking(db , top)
    }


@router.get("/seller_ranking" ,response_model=Seller_rankresponse ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_seller_ranking(db : Session = Depends(get_db) , top : int = 10):
    return {
        "seller_ranking" : get_seller_ranking(db, top)
    }

@router.get("/send_time" ,response_model=Send_time_rateresponse ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_send_rate(db : Session = Depends(get_db)):
    return {
        "send_time_rate" : get_sned_time(db)
    }

@router.get("/products_ranking" ,response_model=Productrankresponse ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_productsranking(db : Session = Depends(get_db) , top : int = 10):
    rank = get_productsranking(db , top)
    return {
        "product_ranking" : rank
    }

@router.get('/alerts' , response_model=ApiResponse[AlertResponse],dependencies=[Depends(require_permission("dashboard:read"))] )
def list_alerts(db : Session = Depends(get_db)):
    alerts = get_alerts(db)
    return ok(alerts)
