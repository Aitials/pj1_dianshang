from app.services.dashboard import get_sales_trend, get_category_ranking_info, get_products_ranking_info
from langchain_core.tools import tool
from pydantic import BaseModel , Field
from langchain.tools import ToolRuntime

class CategoryToolInput(BaseModel):
    top: int = Field(
        description="返回销售额最高的商品类别数量",
        ge=1,
        le=20
    )

class ProductsToolOutput(BaseModel):
    top: int = Field(
        description='返回的商品排行的数量',
        ge = 1,
        le = 20
    )


@tool
def query_sales(runtime :ToolRuntime):
    '''查询电商平台历史销售数据，并分析销售趋势'''
    with runtime.context["session_factory"]() as s:
        return get_sales_trend(s)

@tool(args_schema= CategoryToolInput)
def query_category(runtime  :ToolRuntime ,top : int):
    '''查询商品类别销售额排行'''

    with runtime.context["session_factory"]() as s:
        return get_category_ranking_info(s, top)

@tool(args_schema= ProductsToolOutput)
def query_product(runtime  :ToolRuntime, top : int):
    '''查询商品销售额排行'''
    with runtime.context["session_factory"]() as s:
        return get_products_ranking_info(s, top)
