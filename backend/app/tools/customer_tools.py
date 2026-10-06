from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool
from app.services.customer import get_customer_repurchase_info

@tool
def query_customer(runtime : ToolRuntime):
    '''
    查询客户复购情况，包括总客户数、复购客户数、复购率
    '''
    with runtime.context["session_factory"]() as s:
        return get_customer_repurchase_info(s)
