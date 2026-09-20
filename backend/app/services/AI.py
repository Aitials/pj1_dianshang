import os
import json

from sqlalchemy.orm import Session
from zhipuai import ZhipuAI

from app.tools.dashboard_tools import get_sales_trend_tool


api_key = os.getenv("ZHIPU_API_KEY")

client = ZhipuAI(api_key=api_key)


# =========================
# 1. 告诉 GLM：有哪些工具可以使用
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_trend",
            "description": "获取电商平台按月份统计的销售趋势",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# =========================
# 2. 工具名称 → Python实际函数
# =========================

tools_map = {
    "get_sales_trend": get_sales_trend_tool
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
                "content": "你是一个电商后台运营助手，负责帮助运营人员分析商品、订单、销售和库存等业务问题。回答应该准确、简洁，不确定的信息不要编造。"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        tools=tools,
        tool_choice="required"
    )

    # 查看 GLM 返回的工具调用
    print(response.choices[0].message)

    # -------------------------
    # 4. 获取 GLM 请求调用的工具
    # -------------------------

    tool_call = response.choices[0].message.tool_calls[0]

    tool_name = tool_call.function.name

    # 根据工具名称找到真正的 Python 函数
    tool = tools_map[tool_name]

    # -------------------------
    # 5. 执行真正的业务工具
    # -------------------------

    result = tool(db)

    print(result)

    # -------------------------
    # 6. 把工具结果转换成 JSON
    # -------------------------

    tool_result = json.dumps(
        result,
        ensure_ascii=False,
        default=str
    )

    # -------------------------
    # 7. 第二次请求：让 GLM 分析工具结果
    # -------------------------

    final_response = client.chat.completions.create(
        model="GLM-4.5-Air",
        messages=[
            {
                "role": "system",
                "content": "你是一个电商后台运营助手，负责帮助运营人员分析商品、订单、销售和库存等业务问题。回答应该准确、简洁，不确定的信息不要编造。"
            },
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            }
        ]
    )

    # -------------------------
    # 8. 返回 GLM 最终回答
    # -------------------------

    return final_response.choices[0].message.content