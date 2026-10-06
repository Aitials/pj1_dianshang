from sqlalchemy.orm import Session
from langchain_core.tools import tool
from app.services.customer import get_customer_repurchase_info

@tool(parse_docstring=True)
def query_customer(db: Session):
    '''
    查询客户复购情况，包括总客户数、复购客户数、复购率

    Args:
        db : 要传入Session给会话去查sql
    '''
    return get_customer_repurchase_info(db)
