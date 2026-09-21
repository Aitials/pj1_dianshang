from fastapi import APIRouter, Depends ,HTTPException
from app.api.deps import require_permission
from fastapi import Query
from sqlalchemy.orm import Session
from app.schemas.order import CustomerResponse
from app.schemas.customer import CustomerRankResponse ,CustomerRepurchaseResponse,CustomerGeoResponse
from app.repositories.customer import get_customers , get_customer_by_id,count_customers ,get_customer_rank ,get_customer_repurchase ,get_customer_geo ,get_customer_states
from app.core.response import ok, ok_page
from app.schemas.response import ApiResponse, PageData
from app.db.session import get_db
router = APIRouter()

@router.get('/customers' ,response_model=ApiResponse[PageData[CustomerResponse]], dependencies=[Depends(require_permission("customer:read"))])
def list_customers(page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100),customer_city:str | None = None,customer_state:str | None = None,db: Session = Depends(get_db)):
    customers = get_customers(page ,page_size,customer_city,customer_state,db)
    count = count_customers(customer_city,customer_state,db)
    items = [
        {
            "customer_id": c.customer_id,
            "customer_unique_id": c.customer_unique_id,
            "customer_zip_code_prefix": c.customer_zip_code_prefix,
            "customer_city": c.customer_city,
            "customer_state": c.customer_state,
        }
        for c in customers
    ]

    return ok_page(items,count,page,page_size)

@router.get('/customers/ranking' , response_model=ApiResponse[CustomerRankResponse],dependencies=[Depends(require_permission("customer:read"))])
def list_customer_rank(top: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    rank = get_customer_rank(top,db)
    return ok(rank)

@router.get('/customers/repurchase' ,response_model=ApiResponse[CustomerRepurchaseResponse] ,dependencies=[Depends(require_permission("customer:read"))])
def list_customer_repurchase(db : Session= Depends(get_db)):
    result = get_customer_repurchase(db)
    return ok(result)

@router.get('/customers/geo' ,response_model=ApiResponse[CustomerGeoResponse],dependencies=[Depends(require_permission("customer:read"))])
def list_customer_geo(db: Session = Depends(get_db)):
    geo = get_customer_geo(db)
    return ok(geo)

@router.get('/customers/states' ,response_model=ApiResponse[dict],dependencies=[Depends(require_permission("customer:read"))])
def list_customer_states(db: Session = Depends(get_db)):
    return ok({"states": get_customer_states(db)})



@router.get('/customers/{customer_id}' ,response_model=ApiResponse[CustomerResponse],dependencies=[Depends(require_permission("customer:read"))])
def list_customer_byid( customer_id: str ,db: Session = Depends(get_db)):
    customers = get_customer_by_id(db,customer_id)
    if customers is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return ok(customers)


