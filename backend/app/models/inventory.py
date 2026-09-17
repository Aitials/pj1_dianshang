from sqlalchemy import Column, String,Integer,DateTime
from app.db.session import Base
from sqlalchemy import func

class Inventory(Base):
    __tablename__ = 'inventory'
    product_id = Column(String(35), primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    safety_stock = Column(Integer, nullable=False)

class InventoryLog(Base):
    __tablename__ = 'inventory_log'
    id = Column(Integer, primary_key=True, nullable = False)
    product_id = Column(String(35),nullable = False)
    change = Column(Integer,nullable = False)
    before = Column(Integer,nullable = False)
    after = Column(Integer,nullable = False)
    reason = Column(String(100))
    operator = Column(String(50))
    created_at = Column(DateTime ,default=func.now())
