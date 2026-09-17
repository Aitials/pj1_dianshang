from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.repositories.customer import get_customers , get_customer_by_id

from app.db.session import get_db
router = APIRouter()

@router.get('/customers')
def list_customers(db: Session = Depends(get_db)):
    customers = get_customers(db)
    return {
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

@router.get('/{customer_id}')
def list_customerbyid( customer_id: str ,db: Session = Depends(get_db)):
    customers = get_customer_by_id(db,customer_id)
    return {
        "customer" : customers
    }


