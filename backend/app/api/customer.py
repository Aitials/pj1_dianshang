from fastapi import APIRouter, Depends ,HTTPException
from app.api.deps import require_permission
from sqlalchemy.orm import Session
from app.schemas.order import CustomerResponse
from app.repositories.customer import get_customers , get_customer_by_id,count_customers

from app.db.session import get_db
router = APIRouter()

@router.get('/customers' ,dependencies=[Depends(require_permission("customer:read"))])
def list_customers(page :int,page_size:int ,customer_city:str | None = None,customer_state:str | None = None,db: Session = Depends(get_db)):
    customers = get_customers(page ,page_size,customer_city,customer_state,db)
    count = count_customers(customer_city,customer_state,db)
    return {
        "total": count,
        "customers" : [
            {
                "customer_id": c.customer_id,
                "customer_unique_id": c.customer_unique_id,
                "customer_zip_code_prefix": c.customer_zip_code_prefix,
                "customer_city" : c.customer_city,
                "customer_state" : c.customer_state,
            }
            for c in customers
        ]
    }

@router.get('/customers/{customer_id}' ,response_model=CustomerResponse ,dependencies=[Depends(require_permission("customer:read"))])
def list_customerbyid( customer_id: str ,db: Session = Depends(get_db)):
    customers = get_customer_by_id(db,customer_id)
    if customers is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers


