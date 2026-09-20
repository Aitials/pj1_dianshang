from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session

from app.models.seller import Seller
from app.models.order_items import OrderItem
from app.models.order import Order
from app.models.order_reviews import OrderReview



def get_sellers(page ,page_size,seller_city,seller_state,db: Session):
    stmt = select(Seller)
    if seller_city is not None:
        stmt = stmt.where(Seller.seller_city == seller_city)
    if seller_state is not None:
        stmt = stmt.where(Seller.seller_state == seller_state)
    stmt = stmt.limit(page_size).offset((page -1 ) * page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_seller_byid(db: Session, seller_id: str):
    stmt = select(Seller).where(Seller.seller_id == seller_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def count_sellers(seller_city,seller_state,db: Session):
    stmt = select(func.count(Seller.seller_id))
    if seller_city is not None:
        stmt = stmt.where(Seller.seller_city == seller_city)
    if seller_state is not None:
        stmt = stmt.where(Seller.seller_state == seller_state)
    result = db.execute(stmt).scalar()
    return result

def get_seller_rank(top :int , db: Session):
    stmt = (
        select(func.sum(OrderItem.price).label('sales'),func.count(distinct(Order.order_id)).label('order_count') ,Seller.seller_id)
    .select_from(Seller)
    .join(OrderItem , OrderItem.seller_id == Seller.seller_id)
    .join(Order , OrderItem.order_id == Order.order_id)
    .where(Order.order_status != 'canceled')
    .group_by(Seller.seller_id)
    .order_by(func.sum(OrderItem.price).desc())
    .limit(top)
    )
    rank = db.execute(stmt).all()
    return {
        "top" : top,
        "rank" : [
            {
                "seller_id" : r.seller_id,
                "sales" : r.sales,
                "order_count" : r.order_count,
            }
            for r in rank
        ]
    }

def get_seller_review(db: Session ,top):
    stmt = (
        select(Seller.seller_id,
               func.avg(OrderReview.review_score).label('avg_score'),
               func.count(distinct(OrderReview.review_id)).label('count'))
        .select_from(Seller)
        .join(OrderItem, OrderItem.seller_id == Seller.seller_id)
        .join(Order, OrderItem.order_id == Order.order_id)
        .join(OrderReview , OrderReview.order_id == Order.order_id)
        .where(Order.order_status != 'canceled')
        .group_by(Seller.seller_id)
        .order_by(func.count(distinct(OrderReview.review_id)).desc())
        .limit(top)
    )
    review = db.execute(stmt).all()
    return {
        "top" : top,
        "review_rank" : [
            {
                "seller_id" : r.seller_id,
                "avg_score" : round(r.avg_score,2),
                "review_count" : r.count,
            }
            for r in review
        ]
    }

def get_seller_states(db: Session):
    stmt = (
        select(distinct(Seller.seller_state))
        .where(Seller.seller_state.isnot(None))
        .order_by(Seller.seller_state)
    )
    return [r[0] for r in db.execute(stmt).all()]


