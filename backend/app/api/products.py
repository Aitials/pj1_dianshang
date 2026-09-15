from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.products import get_products

router = APIRouter()

@router.get("/products")
def get_product(db: Session = Depends(get_db)):
    products = get_products(db)
    return {
        "products": [
            {
                "products_id": p.product_id,
                "product_category_name" : p.product_category_name,
                "product_name_length" : p.product_name_length,
                "product_description_length" : p.product_description_length,
                "product_photos_qty" : p.product_photos_qty,
                "product_weight_g" : p.product_weight_g,
                "product_length_cm" : p.product_length_cm,
                "product_height_cm" : p.product_height_cm,
                "product_width_cm" : p.product_width_cm,
            }
            for p in products
        ]
    }
