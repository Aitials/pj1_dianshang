from sqlalchemy import Column, Integer, String , DateTime , Numeric
from app.db.session import Base

class OrderItem(Base):
    __tablename__ = "olist_order_items_dataset_clean"
    order_id = Column(String (35), primary_key=True ,nullable = False)
    order_item_id = Column(Integer, primary_key=True ,nullable = False)
    product_id = Column(String(35) , nullable = False)
    seller_id = Column(String(35), nullable = False)
    shipping_limit_date = Column(DateTime, nullable = False)
    price = Column(Numeric(12,2), nullable = False)
    freight_value = Column(Numeric(12,2), nullable = False)