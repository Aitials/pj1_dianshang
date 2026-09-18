from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from app.schemas.seller import SellerResponse
from app.db.session import get_db
from app.repositories.seller import get_sellers ,count_sellers
from app.repositories.seller import get_seller_byid
from app.api.deps import require_permission
router = APIRouter()


@router.get("/sellers" ,dependencies=[Depends(require_permission("seller:read"))])
def list_sellers(page:int ,page_size :int,seller_city:str | None = None,seller_state :str | None = None ,db: Session = Depends(get_db)):
    sellers = get_sellers(page ,page_size,seller_city,seller_state,db)
    count = count_sellers(seller_city,seller_state,db)
    return {
        "total":count,
        "sellers": [
            {
                "seller_id": s.seller_id,
                "seller_zip_code_prefix": s.seller_zip_code_prefix,
                "seller_city": s.seller_city,
                "seller_state": s.seller_state,
            }
            for s in sellers
        ]
    }

@router.get("/sellers/{seller_id}" , response_model=SellerResponse ,dependencies=[Depends(require_permission("seller:read"))])
def list_seller(seller_id: str, db: Session = Depends(get_db)):
    sellers = get_seller_byid(db, seller_id)
    if sellers is None:
        raise HTTPException(status_code=404, detail="Seller Not Found !")
    return sellers

