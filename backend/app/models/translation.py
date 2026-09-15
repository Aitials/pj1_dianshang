from sqlalchemy import Column, String
from app.db.session import Base

class Translation(Base):
    __tablename__ = "product_category_name_translation_clean"
    product_category_name = Column(String(50) , primary_key=True , nullable=False)
    product_category_name_english = Column(String(50) , nullable=False)

