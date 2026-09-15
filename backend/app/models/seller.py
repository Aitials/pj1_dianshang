from sqlalchemy import Column, String

from app.db.session import Base


class Seller(Base):
    __tablename__ = "olist_sellers_dataset_clean"

    seller_id = Column(String(35), primary_key=True)
    seller_zip_code_prefix = Column(String(5), nullable=False)
    seller_city = Column(String(50), nullable=False)
    seller_state = Column(String(2), nullable=False)
