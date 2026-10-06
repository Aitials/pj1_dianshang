from langgraph.prebuilt import ToolRuntime
from sqlalchemy.orm import Session
from langchain.tools import tool
from app.services.inventory import get_inventory_warning

@tool
def query_inventory_warning(runtime : ToolRuntime):
    '''查询库存数量低于预警线的库存商品，返回库存数量低的商品名字清单'''
    with runtime.context["session_factory"]() as s:
        warning = get_inventory_warning(s)
    return {
        "total": len(warning),
        "items": warning[:15],
    }
