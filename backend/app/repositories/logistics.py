from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order


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
