from fastapi import APIRouter, Depends ,HTTPException ,Query
from sqlalchemy.orm import Session
from app.schemas.seller import SellerResponse ,SellerRankResponse ,Seller_reviewResoinse
from app.db.session import get_db
from app.schemas.response import ApiResponse, PageData
from app.core.response import ok_page, ok
from app.repositories.seller import get_sellers ,count_sellers ,get_seller_rank ,get_seller_review ,get_seller_states
from app.repositories.seller import get_seller_byid
from app.api.deps import require_permission
router = APIRouter()


@router.get("/sellers" , response_model=ApiResponse[PageData[SellerResponse]],dependencies=[Depends(require_permission("seller:read"))])
def list_sellers(page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100),seller_city:str | None = None,seller_state :str | None = None ,db: Session = Depends(get_db)):
    sellers = get_sellers(page ,page_size,seller_city,seller_state,db)
    count = count_sellers(seller_city,seller_state,db)
    items = [
        {
            "seller_id": s.seller_id,
            "seller_zip_code_prefix": s.seller_zip_code_prefix,
            "seller_city": s.seller_city,
            "seller_state": s.seller_state,
        }
        for s in sellers
    ]

    return ok_page(items, count, page, page_size)

@router.get('/sellers/states' ,response_model=ApiResponse[dict],dependencies=[Depends(require_permission("seller:read"))])
def list_seller_states(db: Session = Depends(get_db)):
    return ok({"states": get_seller_states(db)})

@router.get("/sellers/{seller_id}" ,response_model=ApiResponse[SellerResponse],dependencies=[Depends(require_permission("seller:read"))])
def list_seller(seller_id: str, db: Session = Depends(get_db)):
    sellers = get_seller_byid(db, seller_id)
    if sellers is None:
        raise HTTPException(status_code=404, detail="Seller Not Found !")
    return ok(sellers)

@router.get('/seller/rank' ,response_model=ApiResponse[SellerRankResponse],dependencies=[Depends(require_permission("seller:read"))])
def list_seller_rank(top: int = Query(10, ge=1, le=100),db: Session = Depends(get_db)):
    rank = get_seller_rank(top ,db)
    return ok(rank)

@router.get('/seller/review' ,response_model=ApiResponse[Seller_reviewResoinse] ,dependencies=[Depends(require_permission("seller:read"))])
def list_seller_review(db: Session = Depends(get_db), top: int = Query(10, ge=1, le=100)):
    reviews = get_seller_review(db ,top)
    return ok(reviews)