from fastapi import APIRouter ,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.redis import get_cache, set_cache
from app.repositories.dashboard import get_category_ranking,get_seller_ranking,get_sned_time,get_overview ,get_productsranking ,get_alerts
from app.schemas.dashboard import DashboardOverviewResponse ,Productrankresponse ,CategoryRankingResponse ,Seller_rankresponse ,Send_time_rateresponse ,AlertResponse ,TrendResponse
from app.api.deps import require_permission
from app.core.response import ok
from app.schemas.response import ApiResponse
from app.services.dashboard import get_sales_trend
router = APIRouter()

@router.get("/overview" , response_model=ApiResponse[DashboardOverviewResponse] ,dependencies=[Depends(require_permission("dashboard:read"))])
def overview(db: Session = Depends(get_db)):
    cache_key = "dashboard:overview"
    # 1. 先查 Redis
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    # 2. Redis 没有缓存，再查 MySQL
    result = get_overview(db)
    # 3. 把查询结果写入 Redis，缓存 10 分钟
    set_cache(cache_key, result, expire=600)
    # 4. 返回结果
    return ok(result)

@router.get("/trend" ,response_model=ApiResponse[TrendResponse],dependencies=[Depends(require_permission("dashboard:read"))])
def trend(db: Session = Depends(get_db)):
    cache_key = "dashboard:trend"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    trend_data = get_sales_trend(db)
    set_cache(cache_key, {"trend":trend_data}, expire=600)
    return ok({"trend":trend_data})

@router.get("/category-ranking", response_model=ApiResponse[CategoryRankingResponse] ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_category_ranking(db : Session = Depends(get_db) , top : int = 10):
    cache_key = f"dashboard:category-ranking:{top}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    ranking =  get_category_ranking(db , top)
    set_cache(cache_key, {"category_ranking":ranking}, expire=600)
    return ok({"category_ranking" : ranking})


@router.get("/seller_ranking" ,response_model=ApiResponse[Seller_rankresponse] ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_seller_ranking(db : Session = Depends(get_db) , top : int = 10):
    cache_key = f"dashboard:seller-ranking:{top}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    result = get_seller_ranking(db , top)
    set_cache(cache_key,{"seller_ranking": result}, expire=600)
    return ok({
        "seller_ranking" : result
    })

@router.get("/send_time" ,response_model=ApiResponse[Send_time_rateresponse] ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_send_rate(db : Session = Depends(get_db)):
    return ok({
        "send_time_rate" : get_sned_time(db)
    })

@router.get("/products_ranking" ,response_model=ApiResponse[Productrankresponse] ,dependencies=[Depends(require_permission("dashboard:read"))])
def list_productsranking(db : Session = Depends(get_db) , top : int = 10):
    cache_key = f"dashboard:products-ranking:{top}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    rank = get_productsranking(db , top)
    set_cache(cache_key, {"product_ranking":rank}, expire=600)
    return ok({
        "product_ranking" : rank
    })

@router.get('/alerts' , response_model=ApiResponse[AlertResponse],dependencies=[Depends(require_permission("dashboard:read"))] )
def list_alerts(db : Session = Depends(get_db)):
    alerts = get_alerts(db)
    return ok(alerts)
