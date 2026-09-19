from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.geolocation import Geolocation


def get_customers(page ,page_size,customer_city,customer_state,db : Session):
    stmt = select(Customer)
    if customer_city is not None:
        stmt = stmt.where(Customer.customer_city == customer_city)
    if customer_state is not None:
        stmt = stmt.where(Customer.customer_state == customer_state)
    stmt = stmt.limit(page_size).offset((page -1)*page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_customer_by_id(db: Session, customer_id: str):
    stmt = select(Customer).where(Customer.customer_id == customer_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def count_customers(customer_city,customer_state,db: Session):
    stmt =  select(func.count(Customer.customer_id))
    if customer_state is not None:
        stmt = stmt.where(Customer.customer_state == customer_state)
    if customer_city is not None:
        stmt = stmt.where(Customer.customer_city == customer_city)
    result = db.execute(stmt)
    return result.scalar()

def get_customer_rank(top ,db: Session):
    stmt = (select(Customer.customer_unique_id , func.count(distinct(Order.order_id)).label('count_order') ,func.sum(OrderItem.price).label("sales"))
    .select_from(Customer)
    .join(Order ,Order.customer_id == Customer.customer_id)
    .join(OrderItem, OrderItem.order_id == Order.order_id)
    .where(Order.order_status != 'canceled')
    .group_by(Customer.customer_unique_id)
    .order_by(func.sum(OrderItem.price).desc())
    .limit(top)
    )
    result = db.execute(stmt).all()
    return {
        "top":top,
        "customer_rank":[
            {
                "customer_unique_id":r.customer_unique_id,
                "sales" : round(float(r.sales),2),
                "count_order" : r.count_order
            }
            for r in result
        ]
    }

def get_customer_repurchase(db: Session) -> dict:
    # 1. 总客户数：下过单的客户去重
    total_customers = db.execute(
        select(func.count(distinct(Customer.customer_unique_id)))
        .select_from(Customer)
        .join(Order, Order.customer_id == Customer.customer_id)
        .where(Order.order_status != 'canceled')
    ).scalar_one()

    # 2. 复购客户数：先分组找名单，再外层 COUNT
    subq = (
        select(Customer.customer_unique_id)
        .select_from(Customer)
        .join(Order, Order.customer_id == Customer.customer_id)
        .where(Order.order_status != 'canceled')
        .group_by(Customer.customer_unique_id)
        .having(func.count(Order.order_id) >= 2)
        .subquery()
    )
    repeat_customers = db.execute(
        select(func.count()).select_from(subq)
    ).scalar_one()

    # 3. 复购率
    rate = 0.0 if total_customers == 0 else round(repeat_customers / total_customers * 100, 2)

    return {
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "repurchase_rate": rate,
    }


def get_customer_geo(db: Session):
    stmt = (select(Customer.customer_city ,Customer.customer_state,
                   func.avg(Geolocation.geolocation_lat).label('lat'),
                   func.avg(Geolocation.geolocation_lng).label('lng'),
                   func.count(distinct(Customer.customer_unique_id)).label('count_customers'))
    .select_from(Customer)
    .join(Order, Order.customer_id == Customer.customer_id)
    .join(Geolocation , Geolocation.geolocation_zip_code_prefix == Customer.customer_zip_code_prefix)
    .where(Order.order_status != 'canceled')
    .group_by(Customer.customer_city , Customer.customer_state)
    )
    result = db.execute(stmt).all()
    return {
        "items": [
            {
                "city" : r.customer_city,
                "state" : r.customer_state,
                "customer_count" : r.count_customers,
                "lat" : r.lat,
                "lng" : r.lng,
            }
            for r in result
        ]
    }