from sqlalchemy import Column, Integer, Numeric, String

from app.db.session import Base


class OrderPayment(Base):
    __tablename__ = "olist_order_payments_dataset_clean"

    order_id = Column(String(35), primary_key=True)
    payment_sequential = Column(Integer, primary_key=True)
    payment_type = Column(String(15), nullable=False)
    payment_installments = Column(Integer, nullable=False)
    payment_value = Column(Numeric(12, 2), nullable=False)
