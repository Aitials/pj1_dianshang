from sqlalchemy import Column, Integer, String , Float
from app.db.session import Base

class Geolocation(Base):
    __tablename__ = "olist_geolocation_dataset_clean"
    geolocation_zip_code_prefix = Column(String(5),primary_key= True, nullable=False)
    geolocation_lat = Column(Float,nullable=False)
    geolocation_lng = Column(Float,nullable=False)
    geolocation_city = Column(String(50),nullable=False)
    geolocation_state = Column(String(2),nullable=False)






