from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.translation import get_translations

router = APIRouter()


@router.get("/translation")
def list_translations(db: Session = Depends(get_db)):
    translations = get_translations(db)
    return {
        "translations": [
            {
                "product_category_name": t.product_category_name,
                "product_category_name_english": t.product_category_name_english,
            }
            for t in translations
        ]
    }
