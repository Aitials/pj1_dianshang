from sqlalchemy import Column, Integer, String

from app.db.session import Base


class Product(Base):
    __tablename__ = "olist_products_dataset_clean"

    product_id = Column(String(35), primary_key=True)
    product_category_name = Column(String(50), nullable=False)
    product_name_length = Column(Integer)
    product_description_length = Column(Integer)
    product_photos_qty = Column(Integer)
    product_weight_g = Column(Integer)
    product_length_cm = Column(Integer)
    product_height_cm = Column(Integer)
    product_width_cm = Column(Integer)
