from sqlalchemy import func, distinct
from sqlalchemy import select ,func
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_reviews import OrderReview
from app.models.customer import Customer
from app.models.order_items import OrderItem
from app.models.products import Product
from app.models.order_payments import OrderPayment


def count_orders(db : Session ,order_status =None , start_time = None, end_time = None ):
    stmt = select(func.count(Order.order_id))
    if order_status is not None:
        stmt = stmt.where(Order.order_status == order_status)
    if start_time is not None:
        stmt = stmt.where(Order.order_purchase_timestamp >= start_time)
    if end_time is not None:
        stmt = stmt.where(Order.order_purchase_timestamp <= end_time)
    counts = db.execute(stmt)
    return counts.scalars().one()

def avg_reviews(db : Session):
    stmt = select(func.avg(OrderReview.review_score))
    counts = db.execute(stmt)
    return counts.scalars().one()

def count_customers(db : Session):
    stmt = select(func.count(distinct(Customer.customer_unique_id)))
    counts = db.execute(stmt)
    return counts.scalars().one()

def total_sales(db : Session):
    stmt = select(func.sum(OrderItem.price)).join(Order, OrderItem.order_id == Order.order_id).where(Order.order_status != "canceled")
    result = db.execute(stmt)
    return round(result.scalars().one(),2)

def avg_order_value(db : Session):
    stmt = select(func.count(Order.order_status)).where(Order.order_status != "canceled")
    result = db.execute(stmt).scalars().one()
    return round(total_sales(db) / result , 2)

def sales_trend(db : Session ):
    stmt = (select(
    func.date_format(Order.order_purchase_timestamp, "%Y-%m").label("month"),
    func.sum(OrderItem.price).label("sales"),
    )
    .join(Order, OrderItem.order_id == Order.order_id)
    .where(Order.order_status != "canceled")
    .group_by("month")
    .order_by("month"))
    result = db.execute(stmt)
    return [
        {"month": row[0] ,"sales":row[1]}
        for row in result.all()
    ]

def get_category_ranking(db, top):
    stmt =\
    ( select
        (Product.product_category_name,
         func.sum(OrderItem.price)
         )
    .select_from(Order)
    .join(OrderItem ,OrderItem.order_id == Order.order_id )
    .join(Product, Product.product_id == OrderItem.product_id)
    .where(Order.order_status != "canceled")
    .group_by(Product.product_category_name)
    .order_by(func.sum(OrderItem.price).desc())
    .limit(top)
    )
    result = db.execute(stmt).all()
    return [
        {
        "category_name" : c[0] ,
        "sales" : c[1] }
        for c in result
    ]

def get_seller_ranking(db,top):
    stmt = ( select
        (OrderItem.seller_id ,
         func.sum(OrderItem.price))
        .select_from(Order)
        .join(OrderItem, OrderItem.order_id == Order.order_id)
        .where(Order.order_status != "canceled")
        .group_by(OrderItem.seller_id)
        .order_by(func.sum(OrderItem.price).desc())
        .limit(top)
        )
    result  = db.execute(stmt).all()
    return [
        {
            "seller_id" : row[0] ,
            "sales" : row[1]
        }
        for row in result
    ]

def get_sned_time(db):
    delivered = db.execute(
        select(func.count(Order.order_id)).where(
            Order.order_delivered_customer_date.isnot(None)
        )
    ).scalar()

    on_time = db.execute(
        select(func.count(Order.order_id)).where(
            Order.order_delivered_customer_date <= Order.order_estimated_delivery_date
        )
    ).scalar()

    return round(on_time / delivered * 100, 2)

def get_overview(db):
    total_orders =  select(func.count(Order.order_id))
    delivered_orders = select(func.count(Order.order_id)).where(
    Order.order_status == "delivered")
    canceled_orders = select(func.count(Order.order_id)).where(Order.order_status == "canceled")
    total_sales = select(func.sum(OrderPayment.payment_value))

    tresult = db.execute(total_orders).scalars().one()
    dresult = db.execute(delivered_orders).scalars().one()
    cresult = db.execute(canceled_orders).scalars().one()
    tsresult = db.execute(total_sales).scalars().one()
    return {
        "total_orders": tresult,
        "delivered_orders": dresult,
        "canceled_orders": cresult,
        "total_sales": tsresult,
    }
