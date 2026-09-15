from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.geolocation import Geolocation

def get_geolocations(db: Session):
    stmt = select(Geolocation)
    result = db.execute(stmt)
    return result.scalars().all()
