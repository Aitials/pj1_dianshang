from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from app.schemas.product import ProductResponse
from app.db.session import get_db
from app.repositories.products import get_products,get_products_byid,count_products

router = APIRouter()


@router.get("/products")
def list_products(page: int , page_size: int ,product_category_name :str | None = None,db: Session = Depends(get_db)):
    products = get_products(page,page_size,product_category_name,db)
    count = count_products(product_category_name,db)
    return {
        "total": count,
        "items": [
            {
                "product_id": p.product_id,
                "product_category_name": p.product_category_name,
                "product_name_length": p.product_name_length,
                "product_description_length": p.product_description_length,
                "product_photos_qty": p.product_photos_qty,
                "product_weight_g": p.product_weight_g,
                "product_length_cm": p.product_length_cm,
                "product_height_cm": p.product_height_cm,
                "product_width_cm": p.product_width_cm,
            }
            for p in products
        ]
    }


@router.get("/products/{products_id}" ,response_model=ProductResponse)
def list_product_byid(products_id : str ,db: Session = Depends(get_db)):
    products = get_products_byid(products_id ,db)
    if products is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return products