from fastapi import APIRouter ,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.dashboard import count_orders, avg_reviews, count_customers,total_sales,avg_order_value,sales_trend,get_category_ranking,get_seller_ranking,get_sned_time


router = APIRouter()

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return {
        "total_orders": count_orders(db),
        "avg_review_score" : avg_reviews(db),
        "total_customers" : count_customers(db),
        "total_sales" : total_sales(db),
        "avg_order_value" : avg_order_value(db),
    }

@router.get("/trend")
def trend(db: Session = Depends(get_db)):
    return {
        "trend" : sales_trend(db),
    }

@router.get("/category-ranking")
def list_category_ranking(db : Session = Depends(get_db) , top : int = 10):
    return {
        "category_ranking" : get_category_ranking(db, top)
    }


@router.get("/seller-ranking")
def list_seller_ranking(db : Session = Depends(get_db) , top : int = 10):
    return {
        "seller-ranking" : get_seller_ranking(db, top)
    }

@router.get("/send_time")
def list_send_rate(db : Session = Depends(get_db)):
    return {
        "sand_in_time_rate" : get_sned_time(db)
    }
