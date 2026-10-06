from app.services.dashboard import get_sales_trend, get_category_ranking_info, get_products_ranking_info
from langchain_core.tools import tool
from pydantic import BaseModel , Field

class CategoryToolInput(BaseModel):
    top: int = Field(
        description="返回销售额最高的商品类别数量",
        ge=1,
        le=20
    )

def query_sales(db):
    return get_sales_trend(db)

@tool(parse_docstring=True , args_schema= CategoryToolInput)
def query_category(top):
    '''
    查询商品类别销售额排行

    Args:
        top : 商品类别的排名数量
    '''
    return get_category_ranking_info(db, top)


def query_product(db, top):
    return get_products_ranking_info(db, top)
