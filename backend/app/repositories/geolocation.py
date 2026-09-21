from sqlalchemy import select ,func
from sqlalchemy.orm import Session

from app.models.geolocation import Geolocation

def get_geolocations(page ,page_size,db: Session):
    stmt = (select(Geolocation)
            .limit(page_size)
            .offset((page -1)*page_size))
    count = (
        select(func.count())
        .select_from(Geolocation)
        )

    result = db.execute(stmt).scalars().all()
    total = db.execute(count).scalar_one_or_none()
    return result , total
