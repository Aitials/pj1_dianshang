from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.logistics import get_logistics_overview

router = APIRouter()


@router.get("/logistics/overview")
def logistics_overview(db: Session = Depends(get_db)):
    return get_logistics_overview(db)
