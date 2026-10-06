import os
import json
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage , HumanMessage
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from app.db.session import SessionLocal
from app.tools.dashboard_tools import query_sales ,query_product ,query_category
from app.tools.order_tools import query_order_status
from app.tools.inventory_tools import query_inventory_warning
from app.tools.review_tools import query_review
from app.tools.logistics_tools import query_logistics
from app.tools.customer_tools import query_customer
from app.tools.web_search import query_web
from app.models.ai_analysis import AiAnalysis
from langchain.agents import create_agent

#AI系统的提示词
SYSTEM_PROMPT = """
你是一个电商后台运营助手，负责帮助运营人员分析商品、订单、销售、库存、客户和物流等业务问题。

数据规则：
1. 系统内部业务数据来自 Olist 巴西电商历史数据集。
2. 内部数据时间范围主要为 2016-09 至 2018-10。
3. 内部数据属于历史数据，不得描述为当前实时数据。
4. 使用内部工具获得的数据时，应明确说明数据来源和时间范围。
5. 当前网络信息、系统内部历史数据和模型自身推理必须明确区分。
6. 不确定的信息不要编造。

工具使用规则：
1. 用户询问系统内部业务数据时，应优先调用对应业务工具。
2. 不要调用与用户问题无关的工具。
3. 工具返回的数据是事实依据，最终回答应基于工具结果进行分析。
4. 如果数据不足以回答问题，应明确说明，而不是自行编造。
5. 用户询问当前政策、行业新闻、最新动态等外部实时信息时，应调用 web_search 工具联网搜索。
6. 联网搜索结果属于"当前外部信息"，回答时必须与内部历史数据（2016-2018）明确区分，不能混淆。


回答要求：
1. 回答准确、简洁、易于运营人员理解。
2. 涉及历史业务数据时，注明数据时间范围。
3. 可以根据数据进行合理分析和推断，但要明确这是分析或推断，而不是原始事实。
"""

load_dotenv(override=True)
ZHIPUAPI = os.getenv('ZHIPU_API_KEY')
BASR_URL = os.getenv('ZHIPU_BASE_URL')
zhipu = ChatOpenAI(
    api_key = ZHIPUAPI ,
    base_url = BASR_URL,
    model = 'GLM-4.5-Air'
)


AGENT = create_agent(
    model=zhipu,
    tools=[query_category ,
           query_sales ,
           query_product ,
           query_order_status ,
           query_inventory_warning,
           query_review ,
           query_logistics ,
           query_customer,
           query_web],
    system_prompt=SYSTEM_PROMPT,
)


def chat(message: str, db: Session):
    result = AGENT.invoke(
        {"messages": [HumanMessage(content=message)]},
        context={"session_factory": SessionLocal},
    )
    return result["messages"][-1].content