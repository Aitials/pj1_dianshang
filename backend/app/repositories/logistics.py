from sqlalchemy import func, select ,case ,text
from sqlalchemy.orm import Session
from app.models.order_reviews import OrderReview
from app.models.order import Order
from app.models.customer import Customer


def get_logistics_overview(db: Session):
    # 平均履约时长（下单 → 实际送达的天数）
    avg_days = db.execute(
        select(
            func.avg(
                func.datediff(
                    Order.order_delivered_customer_date,
                    Order.order_purchase_timestamp,
                )
            )
        ).where(Order.order_delivered_customer_date.isnot(None))
    ).scalar()

    # 已送达订单数
    delivered = db.execute(
        select(func.count(Order.order_id)).where(
            Order.order_delivered_customer_date.isnot(None)
        )
    ).scalar()

    # 准时订单数（实际 ≤ 预计）
    on_time = db.execute(
        select(func.count(Order.order_id)).where(
            Order.order_delivered_customer_date <= Order.order_estimated_delivery_date
        )
    ).scalar()

    # 延迟订单数（实际 > 预计）
    delayed = db.execute(
        select(func.count(Order.order_id)).where(
            Order.order_delivered_customer_date > Order.order_estimated_delivery_date
        )
    ).scalar()

    return {
        "avg_delivery_days": round(float(avg_days or 0), 2),
        "total_delivered": delivered,
        "on_time_count": on_time,
        "delayed_count": delayed,
        "on_time_rate": round(on_time / delivered * 100, 2) if delivered else 0,
        "delay_rate": round(delayed / delivered * 100, 2) if delivered else 0,
    }

def get_logistics_geo(db : Session):
    fulfillment_days = (func.timestampdiff(text("SECOND"), Order.order_purchase_timestamp ,Order.order_delivered_customer_date) / 86400)
    delay_count = func.sum(case ( (Order.order_delivered_customer_date> Order.order_estimated_delivery_date,1),else_=0))
    stmt = (
        select(Customer.customer_state.label('state'),
            func.count(Order.order_id).label("count"),
            func.avg(fulfillment_days).label("avg_fulfillment_days"),
            (delay_count / func.count(Order.order_id)).label("delay_rate"),)
        .select_from(Order)
        .join(Customer, Customer.customer_id == Order.customer_id)
        .where(Order.order_status != 'canceled',)
        .group_by(Customer.customer_state)
        .order_by(func.count(Order.order_id).desc())
    )
    result = db.execute(stmt).all()
    return {
        "geo":[
        {
            "state": r.state,
            "order_count": r.count,
            "avg_fulfillment_days": round(float(r.avg_fulfillment_days), 2),
            "delay_rate": round(float(r.delay_rate) * 100, 2)
        }
        for r in result
    ]}

def get_delay_rating(db: Session):
    delay_status = case(
        (
            Order.order_delivered_customer_date
            > Order.order_estimated_delivery_date,
            "delayed"
        ),
        else_="on_time"
    ).label("status")

    stmt = (
        select(
            delay_status,
            func.avg(OrderReview.review_score).label("avg_score"),
            func.count(OrderReview.review_id).label("review_count")
        )
        .select_from(Order)
        .join(OrderReview,Order.order_id == OrderReview.order_id)
        .where(
            Order.order_status != "canceled",
            Order.order_delivered_customer_date.is_not(None),
            Order.order_estimated_delivery_date.is_not(None)
        )
        .group_by(delay_status)
    )

    result = db.execute(stmt).all()
    data = {
        "on_time_avg_score": 0,
        "delayed_avg_score": 0,
        "on_time_count": 0,
        "delayed_count": 0
    }

    for r in result:
        if r.status == "on_time":
            data["on_time_avg_score"] = round(float(r.avg_score), 2)
            data["on_time_count"] = r.review_count
        elif r.status == "delayed":
            data["delayed_avg_score"] = round(float(r.avg_score), 2)
            data["delayed_count"] = r.review_count

    return data