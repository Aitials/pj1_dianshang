from langgraph.prebuilt import ToolRuntime
from sqlalchemy.orm import Session
from langchain.tools import tool
from app.services.order import get_order_status

@tool
def query_order_status(runtime :ToolRuntime):
    '''查询订单的不同状态和数量，返回不同状态的订单类型和此状态的订单数量'''
    with runtime.context["session_factory"]() as s:
        return get_order_status(s)
