from fastapi import APIRouter, Depends ,Query
from app.api.deps import require_permission ,get_current_user
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import ok ,ok_page
from app.schemas.response import ApiResponse
from app.schemas.inventory import InventoryListResponse ,InventoryitemResponse ,InventoryWarningResponse ,ReplenishResponse ,inventory_logsResponse ,InventoryWarningItem
from app.repositories.inventory import get_inventory,adjust_inventory,get_warnings ,get_replenish ,get_inventory_logs ,get_data
from app.schemas.AdjustInventory import AdjustInventory
from app.core.redis import get_cache, set_cache,delete_cache ,delete_cache_pattern

router = APIRouter()
@router.get("/inventory" , response_model=ApiResponse[InventoryListResponse], dependencies=[Depends(require_permission("inventory:read"))])
def list_inventory(db : Session = Depends(get_db) ,page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100)):
    cache_key = f"inventory:list:page={page}:page_size={page_size}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    result =  get_inventory(db , page , page_size)
    set_cache(cache_key, result ,expire=600)
    return ok(result)

@router.get('/inventory/detail' ,response_model=ApiResponse[InventoryWarningItem] ,dependencies=[Depends(require_permission("inventory:read"))])
def inventory_data(product_id : str ,db : Session = Depends(get_db) ):
    datas = get_data(product_id, db)
    return ok(datas)

@router.post("/adjust/{product_id}/" ,response_model=ApiResponse[InventoryitemResponse])
def list_adjust_inventory(product_id :str , body :AdjustInventory,db : Session = Depends(get_db) , current_user=Depends( require_permission( "inventory:adjust" ) )):
    result =  adjust_inventory(db , product_id , body.change ,body.reason, current_user.username )
    delete_cache("inventory:warnings" )
    delete_cache_pattern("inventory:replenish:*" ,"inventory:list:*")
    return ok(result)

@router.get("/inventory/warnings" ,response_model=ApiResponse[InventoryWarningResponse],dependencies=[Depends(require_permission("inventory:read"))])
def list_warnigns(db : Session = Depends(get_db)):
    cache_key = "inventory:warnings"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    result = {
        "need_fill": get_warnings(db)
    }
    set_cache(cache_key, result ,expire=600)
    return ok(result)

@router.get('/inventory/replenish' ,response_model=ApiResponse[ReplenishResponse] ,dependencies=[Depends(require_permission("inventory:read"))] )
def list_replenish(replenish_days:int = Query(30 , ge = 1 ,le = 700) ,db : Session = Depends(get_db)):
    cache_key = f"inventory:replenish:{replenish_days}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return ok(cached_data)
    replenish =get_replenish( replenish_days, db)
    set_cache(cache_key, replenish ,expire=600)
    return ok(replenish)

@router.get('/inventory/logs' , response_model=ApiResponse[inventory_logsResponse] ,dependencies=[Depends(require_permission("inventory:read"))])
def list_logs(product_id :str,page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100),db : Session = Depends(get_db)):
    logs = get_inventory_logs(product_id , page , page_size, db)
    return ok_page( logs['items'],logs['total']  ,page ,page_size)