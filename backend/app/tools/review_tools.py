from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from sqlalchemy.orm import Session

from app.services.reviews import get_avg_reviews

@tool
def query_review(runtime : ToolRuntime):
    '''查询全部订单的整体客户评价的平均分，得到整体的评价满意度'''
    with runtime.context["session_factory"]() as s:
        return {
            "avg_review_score": get_avg_reviews(s)
        }
