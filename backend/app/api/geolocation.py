from fastapi import APIRouter, Depends ,Query
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.session import get_db
from app.repositories.geolocation import get_geolocations
from app.core.response import ok_page

router = APIRouter()

@router.get("/geolocation" ,dependencies=[Depends(require_permission("logistics:read"))])
def list_geolocations(page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100),db: Session = Depends(get_db)):
    geolocations , total = get_geolocations(page ,page_size,db)
    return ok_page(geolocations , total ,page,page_size)



