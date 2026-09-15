from sqlalchemy import Column,String
from app.db.session import Base

class Customer(Base):
    __tablename__ = "olist_customers_dataset_clean"
    customer_id = Column(String(35) , primary_key = True, nullable = False)
    customer_unique_id = Column (String(35) ,nullable = False )
    customer_zip_code_prefix = Column(String(5) , nullable = False)
    customer_city = Column (String (40), nullable = False)
    customer_state = Column (String(2) , nullable = False)




