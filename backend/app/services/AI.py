import os
import json

from sqlalchemy.orm import Session
from zhipuai import ZhipuAI
from app.tools.dashboard_tools import query_sales ,query_category ,query_product
from app.tools.order_tools import query_order_status
from app.tools.inventory_tools import query_inventory_warning
from app.tools.review_tools import query_review
from app.tools.logistics_tools import query_logistics
from app.tools.customer_tools import query_customer
from app.tools.web_search import query_web
from app.models.ai_analysis import AiAnalysis

api_key = os.getenv("ZHIPU_API_KEY")

client = ZhipuAI(api_key=api_key)


#AI具体提示词
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


# =========================
# 1. 告诉 GLM：有哪些工具可以使用
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "query_sales",
            "description": "查询电商平台历史销售数据，并分析销售趋势",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_category",
            "description": "查询商品类别销售额排行",
            "parameters": {
                "type": "object",
                "properties": {
                    "top": {
                        "type": "integer",
                        "description": "返回销售额最高的商品类别数量"
                    }
                },
                "required": ["top"]
            }
        }
    } ,
    {
        "type": "function",
        "function": {
            "name": "query_product",
            "description": "查询商品销售额排行",
            "parameters": {
                "type": "object",
                "properties": {
                    "top": {
                        "type": "integer",
                        "description": "返回销售额最高的商品数量"
                    }
                },
                "required": ["top"]
            }
        }
    } ,
    {
        "type": "function",
        "function": {
            "name": "query_order_status",
            "description": "查询订单的不同状态和数量，返回不同状态的订单类型和此状态的订单数量",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_inventory_warning",
            "description": "查询库存数量低于预警线的库存商品，返回库存数量低的商品名字清单",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    } ,
    {
        "type": "function",
        "function": {
            "name": "query_review",
            "description": "查询全部订单的整体客户评价的平均分，得到整体的评价满意度",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_logistics",
            "description": "查询物流履约情况，包括准时率、延迟率、平均履约时长等",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_customer",
            "description": "查询客户复购情况，包括总客户数、复购客户数、复购率",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    } ,
    {
        "type": "function",
        "function": {
            "name": "query_web",
            "description": "联网搜索当前电商政策、行业新闻等外部实时信息，用于回答涉及当下政策/新闻的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                    "type": "string",
                    "description": "要搜索的关键词或问题"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# =========================
# 2. 工具名称 → Python实际函数
# =========================

tools_map = {
    "query_sales": query_sales,
    "query_category" : query_category,
    "query_product" : query_product,
    "query_order_status" : query_order_status,
    "query_inventory_warning" : query_inventory_warning,
    "query_review" : query_review,
    "query_logistics" : query_logistics,
    "query_customer" : query_customer,
    "query_web" : query_web,
}


# =========================
# 3. AI聊天主流程
# =========================

def chat(message: str, db: Session):

    # -------------------------
    # 第一次请求：让 GLM 判断要不要调用工具
    # -------------------------

    response = client.chat.completions.create(
        model="GLM-4.5-Air",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        tools=tools,
        tool_choice="auto"
    )

    # 查看 GLM 返回的工具调用
    print(response.choices[0].message)

    # -------------------------
    # 4. 获取 GLM 请求调用的工具
    # -------------------------

    tool_calls = response.choices[0].message.tool_calls

    if not tool_calls:
        return response.choices[0].message.content

    # -------------------------
    # 5. 遍历所有工具调用，逐个执行，收集结果
    # -------------------------

    tool_results = []
    for tc in tool_calls:
        tool_name = tc.function.name
        tool = tools_map[tool_name]
        arguments = json.loads(tc.function.arguments)
        result = tool(db, **arguments)
        print(result)
        tool_results.append({
            "id": tc.id,
            "content": json.dumps(result, ensure_ascii=False, default=str),
        })

    # -------------------------
    # 6. 第二次请求：让 GLM 分析所有工具结果
    # -------------------------

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        },
    ]
    for tr in tool_results:
        messages.append({
            "role": "tool",
            "tool_call_id": tr["id"],
            "content": tr["content"],
        })

    final_response = client.chat.completions.create(
        model="GLM-4.5-Air",
        messages=messages,
    )

    # -------------------------
    # 7. 返回 GLM 最终回答
    # -------------------------

    final_answer = final_response.choices[0].message.content

    # 记录 AI 问答到 ai_analysis 表
    record = AiAnalysis(
        user_id=None,
        question=message,
        tool_context=json.dumps(
            [
                {
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments) if tc.function.arguments else {},
                }
                for tc in tool_calls
            ],
            ensure_ascii=False,
        ),
        answer=final_answer,
    )
    db.add(record)
    db.commit()

    return final_answer
