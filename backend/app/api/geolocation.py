from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.geolocation import get_geolocations

router = APIRouter()

@router.get("/geolocation")
def list_geolocations(db: Session = Depends(get_db)):
    geolocations = get_geolocations(db)
    return {
        "items" : [
            {"geolocation_zip_code_prefix" : g.geolocation_zip_code_prefix,
             "geolocation_lat" : g.geolocation_lat,
             "geolocation_lng" : g.geolocation_lng,
             "geolocation_city" : g.geolocation_city,
             "geolocation_state" : g.geolocation_state,
             }
            for g in geolocations
        ]
    }
