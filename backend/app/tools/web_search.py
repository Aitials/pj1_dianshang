import os
import hashlib
from zai import ZhipuAiClient
from app.core.redis import get_cache, set_cache


def query_web(db, query):
    # 注意：第一个参数必须是 db（和现有流程 tool(db, **arguments) 对齐，虽然这里用不到）

    # 1. Redis 缓存 key = ai:web:{query 的 md5}
    key = "ai:web:" + hashlib.md5(query.encode("utf-8")).hexdigest()

    # 2. 先查缓存
    cached = get_cache(key)
    if cached is not None:
        return cached

    # 3. 调智谱搜索 API
    client = ZhipuAiClient(api_key=os.getenv("ZHIPU_API_KEY"))
    result = client.web_search.web_search(
        search_engine="search_pro",
        search_query=query,
        count=5,
        content_size="medium",
    )

    # 4. 把结果转成纯 dict（不能直接返回 SDK 对象，否则 json.dumps 会出错）
    data = {"query": query, "results": result.search_result}

    # 5. 写缓存，TTL 1 小时（按成本，别设太长）
    set_cache(key, data, expire=3600)

    return data
