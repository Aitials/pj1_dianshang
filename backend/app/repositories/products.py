from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.models.products import Product


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