import os
import hashlib
import logging

from zai import ZhipuAiClient
from app.core.redis import get_cache, set_cache
from langchain.tools import tool

logger = logging.getLogger("app.tools.web_search")

# 单次网络搜索的超时与重试。
# SDK 默认 timeout 未给出明确上限、max_retries 为内置默认值，
# 外部服务慢或不可达时会把整个 AI 回答拖到超时。这里显式收紧：
#   最坏情况 2 次尝试 × 15s = 30s，仍在 nginx 180s 代理超时之内。
WEB_SEARCH_TIMEOUT = 15.0
WEB_SEARCH_MAX_RETRIES = 1


@tool
def query_web(query : str) -> str :
    '''联网搜索当前电商政策、行业新闻等外部实时信息，用于回答涉及当下政策/新闻的问题'''
    # 1. Redis 缓存 key = ai:web:{query 的 md5}
    key = "ai:web:" + hashlib.md5(query.encode("utf-8")).hexdigest()

    # 2. 先查缓存
    cached = get_cache(key)
    if cached is not None:
        return cached

    # 3. 调智谱搜索 API。
    #    必须包异常：这是本项目唯一直接发外部网络请求的工具，
    #    未捕获时异常会穿透 ToolNode 被上层 AI.chat 的通用 except 吞成
    #    「助手不可用」，用户既拿不到答案也不知道是"搜索挂了"还是"后端坏了"。
    #    改为返回一句给**模型看**的失败说明，让它如实告知用户、不要编造信息。
    try:
        client = ZhipuAiClient(
            api_key=os.getenv("ZHIPU_API_KEY"),
            timeout=WEB_SEARCH_TIMEOUT,
            max_retries=WEB_SEARCH_MAX_RETRIES,
        )
        result = client.web_search.web_search(
            search_engine="search_pro",
            search_query=query,
            count=5,
            content_size="medium",
        )
    except Exception as e:
        logger.warning("联网搜索失败，已降级为告知用户：query=%s err=%s", query, e, exc_info=True)
        return f"联网搜索失败（{type(e).__name__}），暂时无法获取外部实时信息。请如实告知用户本次检索未成功，不要凭训练知识编造当前信息。"

    # 4. 把结果转成纯 dict（不能直接返回 SDK 对象，否则 json.dumps 会出错）
    data = {"query": query, "results": result.search_result}

    # 5. 写缓存，TTL 1 小时（按成本，别设太长）
    set_cache(key, data, expire=3600)

    return data
