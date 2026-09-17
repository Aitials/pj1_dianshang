from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.inventory import get_inventory,adjust_inventory,get_warnings
from app.schemas.AdjustInventory import AdjustInventory

router = APIRouter()
@router.get("/inventory")
def list_inventory(db : Session = Depends(get_db) , page : int = 1, page_size: int = 20):
    return  get_inventory(db , page , page_size)

@router.post("/adjust/{product_id}/")
def list_adjust_inventory(product_id :str , body :AdjustInventory,db : Session = Depends(get_db)):
    return adjust_inventory(db , product_id , body.change ,body.reason, body.operator )

@router.get("/inventory/warnings")
def list_warnigns(db : Session = Depends(get_db)):
    return {
        "need_fill": get_warnings(db)
    }