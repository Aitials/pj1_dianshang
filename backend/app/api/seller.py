from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.seller import get_sellers

router = APIRouter()


@router.get("/sellers")
def list_sellers(db: Session = Depends(get_db)):
    sellers = get_sellers(db)
    return {
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
