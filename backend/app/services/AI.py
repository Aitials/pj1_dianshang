import os
import datetime
import json
import logging
import threading
import uuid
from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from langchain_core.messages import SystemMessage , HumanMessage
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
from langgraph.checkpoint.postgres import PostgresSaver

#AI系统的提示词
SYSTEM_PROMPT = f"""
你是一个电商后台运营助手，负责帮助运营人员分析商品、订单、销售、库存、客户和物流等业务问题。
现在的时间是："{datetime.date.today().isoformat()}",凡涉及"现在""目前""最新""现任"的问题，一律以实时检索结果为准。
与运营无关的提问你可以直接不回答，固定输出‘这个问题我还不知道哦~’
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
5. 用户询问当前政策、行业新闻、最新动态等外部实时信息时，应调用 query_web 工具联网搜索。
6. 联网搜索结果属于"当前外部信息"，回答时必须与内部历史数据（2016-2018）明确区分，不能混淆。
7. 当联网搜索结果与你自身的训练知识冲突时，一律以搜索结果为准。你的训练知识有截止时间，可能已经过时；不要用自身知识去否定或"修正"搜索结果。

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

AGENT_DB_URL = os.getenv('AGENT_DB_URL')

# Postgres 连接超时（秒）。必须显式设置：psycopg 默认 connect_timeout=0 表示**不限**，
# 网络层"黑洞"式不可达时连接会永久挂住，而不是报错返回。
AGENT_DB_CONNECT_TIMEOUT = 10

logger = logging.getLogger("app.ai")

# checkpointer 惰性单例。
#
# 这里刻意**不在导入期连库**：原来是在模块顶层执行
#     checkpointer_cm = PostgresSaver.from_conn_string(AGENT_DB_URL)
#     checkpointer = checkpointer_cm.__enter__()   # 这一行才真正建连接
# 而 app/main.py 顶层 `from app.api.AI import router` 会连带导入本模块。
# 于是 AI 用的这个 Postgres 一旦不可达，**导入期就抛异常/挂住，
# 整个 FastAPI 应用（含 /healthy、登录、订单等全部接口）都起不来** —— 已实测：
# 库不可达时 `import app.services.AI` 阻塞超过 120 秒不返回。
# 改为首次真正用到时才连，让"AI 功能不可用"不再等于"整个服务不可用"。
_checkpointer = None
_checkpointer_cm = None
_checkpointer_lock = threading.Lock()


def _with_connect_timeout(url: str) -> str:
    """给连接串补上 connect_timeout，不覆盖用户显式配置的值。

    先解析成参数字典再重建，不用字符串拼接：连接串里可能已有 query 参数
    （sslmode 等），直接拼 '?...' 会拼坏。
    """
    if not url:
        # 缺配置时原样返回，让 psycopg 在连接时抛出明确的错误，而不是伪装成默认值
        return url
    try:
        params = dict(conninfo_to_dict(url))
    except Exception:
        # 连接串格式非法：原样返回，让后续连接阶段报出真实原因
        return url
    # connect_timeout=0 在 libpq 语义里是"不限"，等同未设置
    if not params.get("connect_timeout"):
        params["connect_timeout"] = str(AGENT_DB_CONNECT_TIMEOUT)
    return make_conninfo(**params)


def _ensure_checkpointer():
    """按需建立 checkpointer 连接并建表；成功后复用连接，失败则抛异常交由调用方处理。"""
    global _checkpointer, _checkpointer_cm

    if _checkpointer is not None:
        return _checkpointer

    with _checkpointer_lock:
        # 双检：等锁期间可能已被其他线程建好
        if _checkpointer is not None:
            return _checkpointer

        cm = PostgresSaver.from_conn_string(_with_connect_timeout(AGENT_DB_URL))
        checkpointer = cm.__enter__()   # 真正建连接
        checkpointer.setup()            # 建表，内部是幂等 DDL

        # 先赋值后返回：setup() 抛异常时连接不进缓存，下次调用会重新尝试，
        # 避免把半成品对象留在全局状态里。
        _checkpointer_cm = cm
        _checkpointer = checkpointer
        return _checkpointer


# 注意：这里**不传 checkpointer**，先建好图。真正的 checkpointer 在首次调用时
# 通过 `AGENT.checkpointer = ...` 注入 —— LangGraph 每次 invoke 都会重新解析
# self.checkpointer（见 langgraph/pregel/main.py 的 _state_checkpointer），
# 因此后置赋值是安全且生效的。
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
    system_prompt = SYSTEM_PROMPT,
)


def chat(message: str , user_id : int , thread_id: str | None = None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    try:
        # 首次调用时才连 checkpointer 库。
        # 单独包一层：连接/建表失败要说清楚是"记忆存储不可用"，
        # 而不是被下面通用异常吞成一句"助手不可用"，便于排障。
        AGENT.checkpointer = _ensure_checkpointer()
    except Exception as e:
        logger.error("AI checkpointer 初始化失败，记忆存储不可用：%s", e, exc_info=True)
        return "Agent助手现在暂时不可用~"

    try:
        result = AGENT.invoke(
            {"messages": [HumanMessage(content=message)]},
            context={"session_factory": SessionLocal},
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )
    except Exception as e:
        logger.error("Agent 调用失败：%s", e, exc_info=True)
        return "Agent助手现在暂时不可用~"

    tool_context = []

    for msg in result["messages"]:
        for tc in getattr(msg, "tool_calls", []):
            tool_context.append({
                "name": tc["name"],
                "arguments": tc.get("args", {}),
            })

    final_answer = result["messages"][-1].content


    try:
        with SessionLocal() as db:
            record = AiAnalysis(
                user_id=user_id,
                question=message,
                tool_context=json.dumps(
                    tool_context,
                    ensure_ascii=False,
                ),
                answer=final_answer,
            )
            db.add(record)
            db.commit()
    except Exception as e:
        print('Ai日志写入失败!' + str(e))
        pass

    return {
        'answer': final_answer,
        "thread_id": thread_id,
    }
