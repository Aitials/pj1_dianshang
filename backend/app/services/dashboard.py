from app.repositories.dashboard import sales_trend
from sqlalchemy.orm import Session
def get_sales_trend(db :Session):
    return sales_trend(db)