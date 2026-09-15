from sqlalchemy import Column, String,DateTime
from app.db.session import Base

class Order(Base):
    __tablename__ = "olist_orders_dataset_clean"
    order_id = Column(String(35), primary_key=True, nullable=False)
    customer_id = Column(String(35), nullable=False,)
    order_status = Column(String(15), nullable=False)
    order_purchase_timestamp = Column(DateTime, nullable= True)
    order_approved_at = Column(DateTime, nullable= True)
    order_delivered_carrier_date = Column(DateTime, nullable= True)
    order_delivered_customer_date = Column(DateTime, nullable= True)
    order_estimated_delivery_date = Column(DateTime, nullable= True)

