from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from app.services.logistics import get_logistics

@tool
def query_logistics(runtime: ToolRuntime):
    '''查询物流履约情况，包括准时率、延迟率、平均履约时长等'''
    with runtime.context["session_factory"]() as s:
        return get_logistics(s)
