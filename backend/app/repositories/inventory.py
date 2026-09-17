from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from app.models.inventory import Inventory , InventoryLog
from sqlalchemy import func

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