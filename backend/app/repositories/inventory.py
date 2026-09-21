from typing import cast
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from app.models.inventory import Inventory , InventoryLog
from app.models.operation_log import OperationLog
from sqlalchemy import func
from datetime import timedelta
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.inventory import Inventory

def get_inventory(db: Session ,page ,page_size):
    stmt = (
    select(Inventory.quantity  , Inventory.product_id ,Inventory.safety_stock)

    .limit(page_size).offset((page-1) * page_size))
    result = db.execute(stmt).all()
    total = db.execute(select(func.count(Inventory.product_id))).scalar()
    return {
        "total" : total,
        "page" : page,
        "page_size" : page_size,
        "items" : [
            {
                "product_id" : i.product_id,
                "quantity" : i.quantity,
                "safe_stock" : i.safety_stock,
            }
            for i in result
        ]
    }


def adjust_inventory(db : Session , product_id , change ,reason ,operator):
    inv = db.get(Inventory,product_id)
    if inv is None:
        before = 0
        inv = Inventory(product_id=product_id, quantity=0, safety_stock=10)
        db.add(inv)
    else:
        before = inv.quantity
    after = before + change  # 算 after
    inv.quantity = after  # 改 Inventory

    log = InventoryLog(  # 写流水（before 必须给）
        product_id=product_id,
        change=change,
        before=before,
        after=after,
        reason=reason,
        operator=operator,
    )
    db.add(log)

    # 记录操作日志
    op_log = OperationLog(
        operator=operator,
        action="adjust_inventory",
        target=product_id,
        detail=f"change={change}, reason={reason}",
    )
    db.add(op_log)
    db.commit()

    return {"product_id": product_id, "before": before, "after": after}


def get_warnings(db : Session ):
    stmt = (select(Inventory).where(Inventory.quantity <= Inventory.safety_stock))
    result = db.execute(stmt).scalars().all()
    return [
        {
            "product_id" : i.product_id,
            "quantity" : i.quantity,
            "safe_stock" : i.safety_stock,
        }
        for i in result
    ]

def get_replenish(replenish_days, db: Session):
    min_time = db.execute(select(func.min(Order.order_purchase_timestamp))).scalar()
    max_time = db.execute(select(func.max(Order.order_purchase_timestamp))).scalar()
    total_days = (max_time - min_time).days

    stmt = (
        select(OrderItem.product_id,func.count(OrderItem.order_id).label("count")
        )
        .select_from(OrderItem)
        .join(Order,OrderItem.order_id == Order.order_id)
        .where(Order.order_status != "canceled")
        .group_by(OrderItem.product_id)
    )

    result = db.execute(stmt).all()

    # 2. 查询库存
    stmt2 = select(
        Inventory.product_id,
        Inventory.quantity,
        Inventory.safety_stock
    )

    inventory_result = db.execute(stmt2).all()

    # 3. 把库存做成 product_id → 库存信息
    inventory_map = {
        i.product_id: {
            "quantity": i.quantity,
            "safety_stock": i.safety_stock
        }
        for i in inventory_result
    }

    # 4. 合并销量和库存，并计算补货量
    items = []

    for i in result:
        inventory = inventory_map.get(i.product_id)

        if inventory is None:
            continue

        avg_daily_sales = i.count / total_days

        suggest_quantity = max(
            avg_daily_sales * replenish_days
            + inventory["safety_stock"]
            - inventory["quantity"],
            0
        )

        items.append({
            "product_id": i.product_id,
            "avg_daily_sales": round(avg_daily_sales, 2),
            "suggest_quantity": round(suggest_quantity, 0),
            "current_quantity": inventory["quantity"],
            "safety_stock": inventory["safety_stock"]
        })
    items = [i for i in items if i["suggest_quantity"] > 0]
    items.sort(key=lambda x: x["suggest_quantity"], reverse=True)
    return {
        "items": items
    }


def get_inventory_logs( product_id, page, page_size ,db):
    total = (select(func.count(InventoryLog.id)).where(InventoryLog.product_id == product_id))
    stmt = (
        select(InventoryLog)
        .where(InventoryLog.product_id == product_id)
        .order_by(InventoryLog.id.desc())
        .limit(page_size).offset((page - 1) * page_size)
    )
    total_count = db.execute(total).scalar()
    logs = db.scalars(stmt).all()
    return {
        "total" :total_count,
        "page" : page,
        "page_size" : page_size,
        "items" : [
            {
                "id" : i.id,
                "product_id": i.product_id,
                "change" : i.change,
                "before" : i.before,
                "after" : i.after,
                "reason" : i.reason,
                "operator" : i.operator,
                "created_at" : i.created_at,
            }
            for i in logs
        ]
    }

def get_data(product_id, db : Session):
    inv = db.get(Inventory, product_id)
    if inv is None:
        return None
    return {
        "product_id": inv.product_id,
        "quantity": inv.quantity,
        "safe_stock": inv.safety_stock,
    }
