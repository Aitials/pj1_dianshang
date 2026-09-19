from fastapi import APIRouter, Depends
from app.api.deps import require_permission
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import ok
from app.schemas.response import ApiResponse
from app.schemas.inventory import InventoryListResponse ,InventoryitemResponse ,InventoryWarningResponse
from app.repositories.inventory import get_inventory,adjust_inventory,get_warnings
from app.schemas.AdjustInventory import AdjustInventory

router = APIRouter()
@router.get("/inventory" , response_model=ApiResponse[InventoryListResponse], dependencies=[Depends(require_permission("inventory:read"))])
def list_inventory(db : Session = Depends(get_db) , page : int = 1, page_size: int = 20):
    result =  get_inventory(db , page , page_size)
    return ok(result)

@router.post("/adjust/{product_id}/" ,response_model=ApiResponse[InventoryitemResponse], dependencies=[Depends(require_permission("inventory:adjust"))])
def list_adjust_inventory(product_id :str , body :AdjustInventory,db : Session = Depends(get_db)):
    result =  adjust_inventory(db , product_id , body.change ,body.reason, body.operator )
    return ok(result)

@router.get("/inventory/warnings" ,response_model=ApiResponse[InventoryWarningResponse],dependencies=[Depends(require_permission("inventory:read"))])
def list_warnigns(db : Session = Depends(get_db)):
    result = {
        "need_fill": get_warnings(db)
    }
    return ok(result)