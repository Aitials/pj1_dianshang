from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.session import get_db
from app.repositories.logistics import get_logistics_overview

router = APIRouter()


@router.get("/logistics/overview" ,dependencies=[Depends(require_permission("logistics:read"))])
def logistics_overview(db: Session = Depends(get_db)):
    return get_logistics_overview(db)
