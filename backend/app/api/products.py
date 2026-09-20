from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from app.schemas.product import ProductResponse
from app.db.session import get_db
from app.repositories.products import get_products,get_products_byid,count_products ,get_category_analysis ,get_rating_rank
from app.api.deps import require_permission
from app.core.response import ok ,ok_page
from app.schemas.response import ApiResponse, PageData
from app.schemas.product import CategoryanaResponse ,ratingRankResponse ,ProductResponse


router = APIRouter()


@router.get("/products" ,response_model=ApiResponse[PageData[ProductResponse]],dependencies=[Depends(require_permission("product:read"))])
def list_products(page: int , page_size: int ,product_category_name :str | None = None,db: Session = Depends(get_db)):
    products = get_products(page,page_size,product_category_name,db)
    count = count_products(product_category_name,db)
    items = [
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
    return ok_page(items,count ,page ,page_size)

@router.get('/products/category-analysis' ,response_model=ApiResponse[CategoryanaResponse],dependencies=[Depends(require_permission("product:read"))])
def list_category_analysis(db: Session = Depends(get_db) , top : int = 10):
    resul = get_category_analysis(db ,top)
    return ok(resul)

@router.get('/products/rating_rank' ,response_model=ApiResponse[ratingRankResponse] , dependencies=[Depends(require_permission("product:read"))])
def list_rating_rank(top : int = 10 ,order : str ='desc',min_reviews:int = 10,db: Session = Depends(get_db)):
    rank = get_rating_rank(top ,order ,min_reviews ,db)
    return ok(rank)

@router.get("/products/{products_id}" ,response_model=ProductResponse ,dependencies=[Depends(require_permission("product:read"))])
def list_product_byid(products_id : str ,db: Session = Depends(get_db)):
    products = get_products_byid(products_id ,db)
    if products is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return products