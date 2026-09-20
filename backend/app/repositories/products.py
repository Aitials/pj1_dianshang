from unittest import result

from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session
from app.models.products import Product
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.order_reviews import OrderReview

def get_products(page,page_size,product_category_name,db: Session):
    stmt = select(Product)
    if product_category_name is not None:
        stmt = stmt.where(Product.product_category_name == product_category_name)
    stmt = stmt.limit(page_size).offset((page -1)*page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_products_byid( products_id :str, db: Session ):
    stmt = select(Product).where(Product.product_id == products_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def count_products(product_category_name ,db: Session):
    stmt = select(func.count(Product.product_id))
    if product_category_name is not None:
        stmt = stmt.where(Product.product_category_name == product_category_name)
    result = db.execute(stmt).scalar()
    return result

def get_category_analysis(db: Session , top):
    stmt = (
        select( Product.product_category_name, func.sum(OrderItem.price).label('sales') , func.count(distinct(Order.order_id)).label('order_count') ,func.avg(OrderItem.price).label("avg_price"))
        .select_from(Product)
        .join(OrderItem , Product.product_id == OrderItem.product_id)
        .join(Order , OrderItem.order_id == Order.order_id)
        .where(Order.order_status != 'canceled')
        .group_by(Product.product_category_name)
        .order_by(func.sum(OrderItem.price).desc())
        .limit(top)
    )
    result = db.execute(stmt).all()
    return {
        "top" : top,
        "category_analysis" : [
            {
                "category_name" : r.product_category_name,
                "sales":r.sales,
                "order_count":r.order_count,
                "avg_price" : round(r.avg_price,2)
            }
            for r in result
        ]
    }

def get_rating_rank(top: int,order: str,min_reviews: int ,db: Session):
    # 先得到去重后的：product_id + order_id
    product_orders = (
        select(
            OrderItem.product_id,
            OrderItem.order_id
        )
        .join(Order,OrderItem.order_id == Order.order_id)
        .where(Order.order_status != "canceled")
        .distinct()
        .subquery()
    )

    stmt = (
        select(
            product_orders.c.product_id,
            func.avg(OrderReview.review_score).label("avg_score"),
            func.count(OrderReview.review_id).label("review_count")
        )
        .join(OrderReview,product_orders.c.order_id == OrderReview.order_id)
        .group_by(product_orders.c.product_id)
        .having(func.count(OrderReview.review_id) >= min_reviews)
    )

    if order == "asc":
        stmt = stmt.order_by(func.avg(OrderReview.review_score).asc())
    else:
        stmt = stmt.order_by(func.avg(OrderReview.review_score).desc())

    stmt = stmt.limit(top)

    result = db.execute(stmt).all()

    return {
        "top":top,
        "rating_rank" : [
        {
            "product_id": r.product_id,
            "avg_score": round(r.avg_score, 2),
            "review_count": r.review_count
        }
        for r in result
        ]
    }

def get_categories(db: Session):
    stmt = (
        select(distinct(Product.product_category_name))
        .where(Product.product_category_name.isnot(None))
        .order_by(Product.product_category_name)
    )
    return [r[0] for r in db.execute(stmt).all()]






