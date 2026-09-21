# 需求说明书（Requirements Specification）

> 项目：电商运营管理与智能分析平台
> 英文名：E-commerce Operations Management and Intelligent Analytics Platform
> 对应论文章节：需求分析
> 依据：项目总蓝图第 1、2、3、15 章 + 后端 / 前端代码核对
> 原则：本文所有接口路径、权限名、表名均可在代码中定位；未实现或未能核实的项在「已知偏差」中如实标注。

## 1. 项目背景与目标

### 1.1 项目定位

本项目是一个**面向电商运营人员和管理人员的后台管理系统**，不是面向消费者的购物商城。系统基于 Olist Brazilian E-Commerce Public Dataset 建立历史电商业务数据体系，提供订单、商品/类目、客户、卖家、物流、库存的运营管理与分析能力，并在业务系统之上叠加 LLM 智能运营助手（Tool Calling + 联网搜索），形成"看生意—找问题—分析原因—做决策"的一体化后台。

### 1.2 项目边界

| 属于本项目 | 不属于本项目 |
|------------|--------------|
| 电商运营后台 / 管理端 | 面向普通消费者的购物商城 |
| 历史交易数据分析 | 真实线上电商平台的实时交易系统 |
| 订单、类目、客户、卖家、物流、评价分析 | 真实支付扣款系统 |
| 应用自建库存模拟与库存决策 | 真实仓储 WMS 全功能 |
| AI 决策辅助 + Tool Calling + 联网搜索 | 让 AI 独立决定并直接修改生产数据 |
| FastAPI 后端 + MySQL + Redis + Vue 管理端 | 为炫技堆叠无关中间件 |

### 1.3 核心目标

| 编号 | 目标 | 落地载体 |
|------|------|----------|
| G1 | 把原始 CSV 转换为可查询、可分析、可服务的业务数据库 | 9 张 `olist_*_dataset_clean` 业务表 |
| G2 | 交付真正可操作的后台系统，而非只有图表的 BI Dashboard | 前端 15 个业务视图 + 51 条后端路径（`/api` 下 52 个操作） |
| G3 | 通过 CRUD / 聚合统计 / 分页 / 权限 / 缓存体现后端工程能力 | 1 个库存写接口 + RBAC + Redis |
| G4 | AI 调用系统提供的数据工具分析，而非整表投喂模型 | `app/tools/*` 共 9 个工具函数 |
| G5 | AI 结合联网搜索，把历史经营数据与当前外部信息分开引用 | `app/tools/web_search.py` |
| G6 | 全过程沉淀需求/数据/数据库/AI/测试文档，支撑毕业论文 | `docs/` 目录 |

> 术语约定：**有效订单** = `order_status != 'canceled'`（见 `repositories/dashboard.py: total_sales`）；**客户唯一身份** = `customer_unique_id`（用于归并同一客户的多条 `customer_id`）；**库存台账** = 应用自建表 `inventory`（Olist 原始数据无库存字段）。

## 2. 数据来源与规模

| 项目 | 说明 |
|------|------|
| 数据集 | Olist Brazilian E-Commerce Public Dataset（Kaggle 公开数据集） |
| 数据性质 | 匿名化**历史**交易数据，非实时 |
| 订单时间范围 | 2016-09-04 ~ 2018-10-17 |
| 原始文件 | 9 张核心 CSV + 2 个内容重复的 category translation 文件 |
| 数据体量 | 订单 99,441；订单明细 112,650；产品 32,951；卖家 3,095；客户 99,441（唯一身份 96,096）；支付 103,886；评价 99,224；地理约 1,000,163 行（含约 26 万完全重复） |

> 数据研究、字段字典、清洗规则、质量报告分别见 `02_dataset_description.md`、`03_data_dictionary.md`、`04_data_quality_report.md`、`05_data_processing.md`。

**数据对需求的硬性约束**：products 无商品名称 → 商品模块定位为"产品与类目运营分析"，不做商城详情页；原始数据无库存字段 → 库存必须是应用自建模型（`inventory` / `inventory_log`）且不得声称来自 Olist；数据为 2016–2018 历史样本 → AI 必须标注时间范围，涉及当前政策必须联网；评价文本大量缺失 → 空文本不得报错；订单时间字段有缺失 → 允许 NULL 不填补。

## 3. 用户角色与权限需求

### 3.1 需求侧定义的目标用户（设计文档第 3 章）

| 角色 | 核心需求 | 权限诉求 |
|------|----------|----------|
| 运营人员 | 查看销售、订单、类目、库存、客户、物流指标；处理日常运营 | 业务数据读写、库存调整、AI 分析 |
| 运营主管 | 查看整体经营、异常、趋势、团队/卖家表现 | 全部业务分析、导出、AI |
| 系统管理员 | 账号、角色、日志、系统配置 | 系统级权限 |
| AI 助手 | 调用业务工具读取数据并生成建议 | 只读工具为主；禁止默认改库 |

### 3.2 实际落地角色（以代码为准，共 3 个）

代码中不存在角色枚举常量，角色以**数据行**形式存储在 `system_role` 表，由 `system_user_role` 关联用户；前端 `frontend/src/stores/auth.js: ROLE_MENUS` 固化了三个角色的菜单可见范围：

| 角色名 | 可访问菜单（`ROLE_MENUS`） | 前端路由 |
|--------|---------------------------|----------|
| `admin` | 全部 10 个菜单 | `/dashboard`、`/orders`、`/products`、`/customers`、`/sellers`、`/logistics`、`/inventory`、`/ai`、`/users`、`/logs` |
| `operator` | 7 个业务菜单（无库存、无系统管理） | `/dashboard`、`/orders`、`/products`、`/customers`、`/sellers`、`/logistics`、`/ai` |
| `warehouse` | 3 个菜单 | `/products`、`/inventory`、`/ai` |

> 说明：`warehouse` 角色未分配 `dashboard:read`，因此前端根路径 `/` 的重定向不能固定写 `/dashboard`，已改为"落到该角色第一个可访问菜单"（见 `frontend/src/router/index.js` 的 `redirect`），否则会被路由守卫拦截并弹"没有权限"。

### 3.3 RBAC 需求

| 需求 | 说明 | 落地 |
|------|------|------|
| 用户与角色解耦 | 用户不直接挂权限 | `system_user_role` 中间表 |
| 角色与权限解耦 | 角色授权按权限项配置 | `system_role_permission` 中间表 |
| 接口级鉴权 | 每个受保护接口声明所需权限 | `Depends(require_permission("<name>"))` |
| 前端菜单按角色隐藏 | 越权菜单不可见 | `MainLayout.vue` 按 `ROLE_MENUS` 过滤 |

## 4. 功能性需求

模块编号约定：`FR-<模块>-<序号>`。所有接口路径均可在 `backend/app/api/*.py` 中检索到。

### 4.1 认证与权限（FR-AUTH）

| 需求编号 | 需求描述 | 对应接口 | 权限 |
|----------|----------|----------|------|
| FR-AUTH-01 | 用户以用户名+密码登录，成功后签发 JWT | `POST /api/auth/login` | 无（公开） |
| FR-AUTH-02 | 前端持久化 token 并在后续请求自动携带 `Authorization: Bearer` | `frontend/src/utils/request.js` | — |
| FR-AUTH-03 | 提供注册接口创建账号 | `POST /api/auth/register` | 无（公开） |
| FR-AUTH-04 | 查询当前登录用户的用户名与角色列表 | `GET /api/auth/me` | 已登录 |
| FR-AUTH-05 | token 过期或非法时返回 401 并由前端跳转登录页 | `app/api/deps.py: get_current_user` | — |
| FR-AUTH-06 | 无权限访问时返回 403 | `require_permission` | — |

对应页面：`Login.vue`。

### 4.2 经营总览 Dashboard（FR-DASH）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-DASH-01 | 核心指标卡：销售额、订单量、客单价、客户数、平均评分、准时率 | `GET /api/dashboard/overview` | `Dashboard.vue` |
| FR-DASH-02 | 月度/日度销售趋势 | `GET /api/dashboard/trend` | `Dashboard.vue` |
| FR-DASH-03 | 类目销售排行 Top N | `GET /api/dashboard/category-ranking?top=10` | `Dashboard.vue` |
| FR-DASH-04 | 卖家销售排行 Top N | `GET /api/dashboard/seller_ranking?top=10` | `Dashboard.vue` |
| FR-DASH-05 | 商品销售排行 Top N | `GET /api/dashboard/products_ranking?top=10` | `Dashboard.vue` |
| FR-DASH-06 | 准时交付率 | `GET /api/dashboard/send_time` | `Dashboard.vue` |
| FR-DASH-07 | 预警聚合：低库存 / 高延迟 / 低评分 | `GET /api/dashboard/alerts` | `Dashboard.vue` |
| FR-DASH-08 | 高频聚合结果缓存，减少重复计算 | Redis（`dashboard:*` key） | — |

指标口径（`app/repositories/dashboard.py`）：

- 销售额 `total_sales` = `SUM(order_items.price)` JOIN orders，且 `order_status != 'canceled'`；
- 客单价 `avg_order_value` = 销售额 ÷ 非取消订单数；
- 客户数 `count_customers` = `COUNT(DISTINCT customer_unique_id)`；
- 平均评分 `avg_reviews` = `AVG(review_score)` 保留 2 位；
- 销售趋势 `sales_trend` = 按 `DATE_FORMAT(order_purchase_timestamp, '%Y-%m')` 分组求和。

> 设计文档要求"必要时区分取消/有效订单"，已在销售额与客单价中实现；但订单量指标 `count_orders` 未默认排除取消订单，需由调用方传 `order_status` 过滤，属于口径待明确项。

### 4.3 订单管理（FR-ORD）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-ORD-01 | 订单分页列表，支持状态、时间区间筛选 | `GET /api/orders?page&page_size&order_status&start_time&end_time` | `Orders.vue` |
| FR-ORD-02 | 订单状态分布统计 | `GET /api/orders/status-distribution` | `Orders.vue` |
| FR-ORD-03 | 订单月度趋势 | `GET /api/orders/monthly-trend` | `Orders.vue` |
| FR-ORD-04 | 订单详情：订单概况 + 客户 + 商品明细 + 支付 + 评价 | `GET /api/orders/{order_id}` | `OrderDetail.vue` |
| FR-ORD-05 | 订单不存在时返回 404 | 同上（`HTTPException(404)`） | — |

### 4.4 商品与类目（FR-PROD）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-PROD-01 | 产品分页列表，支持按类目筛选 | `GET /api/products?page&page_size&product_category_name` | `Products.vue` |
| FR-PROD-02 | 产品详情（属性 + 运营指标） | `GET /api/products/{products_id}` | `ProductDetail.vue` |
| FR-PROD-03 | 类目销售分析 Top N | `GET /api/products/category-analysis?top=10` | `Products.vue` |
| FR-PROD-04 | 类目评分排行，支持升/降序与最小评价数门槛 | `GET /api/products/rating_rank?top&order&min_reviews` | `Products.vue` |
| FR-PROD-05 | 类目清单（葡语 + 英语） | `GET /api/products/categories` | `Products.vue` |

### 4.5 客户分析（FR-CUST）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-CUST-01 | 客户分页列表，支持城市/州筛选 | `GET /api/customers?page&page_size&customer_city&customer_state` | `Customers.vue` |
| FR-CUST-02 | 客户详情 | `GET /api/customers/{customer_id}` | `CustomerDetail.vue` |
| FR-CUST-03 | 客户消费排行 Top N | `GET /api/customers/ranking?top=10` | `Customers.vue` |
| FR-CUST-04 | 复购分析（总客户数 / 复购客户数 / 复购率） | `GET /api/customers/repurchase` | `Customers.vue` |
| FR-CUST-05 | 客户地域分布 | `GET /api/customers/geo` | `Customers.vue` |
| FR-CUST-06 | 州列表（筛选项数据源） | `GET /api/customers/states` | `Customers.vue` |

> 需求要求"用 `customer_unique_id` 识别同一真实客户"，已在 `count_customers`、复购统计中实现；但客户列表与详情接口仍以 `customer_id` 为主键返回，属于口径已实现、粒度待说明项。

### 4.6 卖家分析（FR-SELL）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-SELL-01 | 卖家分页列表，支持城市/州筛选 | `GET /api/sellers?page&page_size&seller_city&seller_state` | `Sellers.vue` |
| FR-SELL-02 | 卖家详情 | `GET /api/sellers/{seller_id}` | `SellerDetail.vue` |
| FR-SELL-03 | 卖家销售排行 Top N | `GET /api/seller/rank?top=10` | `Sellers.vue` |
| FR-SELL-04 | 卖家评分表现 | `GET /api/seller/review?top=20` | `Sellers.vue` |
| FR-SELL-05 | 州列表（筛选项数据源） | `GET /api/sellers/states` | `Sellers.vue` |

> 注意：卖家排行与评价接口使用单数前缀 `/api/seller/...`，与列表接口 `/api/sellers` 不一致，属命名待统一项（前端 `api/sellers.js` 已适配）。

### 4.7 物流分析（FR-LOGI）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-LOGI-01 | 物流总览：发货耗时、运输耗时、履约时长、延迟率 | `GET /api/logistics/overview` | `Logistics.vue` |
| FR-LOGI-02 | 物流地域分布 | `GET /api/logistics/geo` | `Logistics.vue` |
| FR-LOGI-03 | 延迟与评分关联分析 | `GET /api/logistics/delay-rating` | `Logistics.vue` |

### 4.8 库存管理（FR-INV）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-INV-01 | 库存台账分页列表（product_id / quantity / safety_stock） | `GET /api/inventory?page&page_size` | `Inventory.vue` |
| FR-INV-02 | 单品库存明细 | `GET /api/inventory/detail?product_id` | `Inventory.vue` |
| FR-INV-03 | 库存调整：写入调整前后数量、原因、操作人 | `POST /api/adjust/{product_id}/` | `Inventory.vue` |
| FR-INV-04 | 低库存预警（`quantity <= safety_stock`） | `GET /api/inventory/warnings` | `Inventory.vue` |
| FR-INV-05 | 补货建议（历史日均销量 × 补货周期 + 安全库存 − 当前库存） | `GET /api/inventory/replenish?replenish_days=30` | `Inventory.vue` |
| FR-INV-06 | 库存流水查询（分页，按 product_id） | `GET /api/inventory/logs?product_id&page&page_size` | `Inventory.vue` |
| FR-INV-07 | 调整后使库存相关缓存失效 | `delete_cache` / `delete_cache_pattern` | — |
| FR-INV-08 | 调整前后必须满足 `after = before + change` | `repositories/inventory.py: adjust_inventory` | — |
| FR-INV-09 | 调整时同步写入库存流水与操作日志 | `inventory_log` + `operation_log` | — |

### 4.9 AI 运营助手（FR-AI）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-AI-01 | 自然语言问答，返回运营分析结论 | `POST /api/ai/chat` | `AIChat.vue` |
| FR-AI-02 | 模型按需调用业务工具取数（Tool Calling） | `app/tools/*` 共 9 个工具 | — |
| FR-AI-03 | 询问当前政策/新闻时调用联网搜索工具 | `query_web`（智谱 web_search，`search_pro`，count=5） | — |
| FR-AI-04 | 回答须区分内部历史数据（2016–2018）与当前外部信息 | `SYSTEM_PROMPT` 第 5、6 条 | — |
| FR-AI-05 | AI 问答落库留痕（问题、工具调用摘要、回答） | `ai_analysis` 表 | — |
| FR-AI-06 | 联网结果缓存，控制调用成本 | Redis key `ai:web:{md5(query)}`，TTL 3600s | — |
| FR-AI-07 | AI 默认只读，不执行 UPDATE/DELETE | 工具均为查询函数 | — |
| FR-AI-08 | AI 回复在前端渲染前必须消毒，防 XSS | `AIChat.vue: DOMPurify.sanitize` | — |

已注册给模型的 9 个工具（`services/AI.py: tools` / `tools_map`）：

| 工具名 | 入参 | 返回内容 | 实现 |
|--------|------|----------|------|
| `query_sales` | — | 月度销售趋势 | `tools/dashboard_tools.py` |
| `query_category` | `top` | 类目销售额排行 | 同上 |
| `query_product` | `top` | 商品销售额排行 | 同上 |
| `query_order_status` | — | 订单状态分布 | `tools/order_tools.py` |
| `query_inventory_warning` | — | 低库存清单（前 15 条） | `tools/inventory_tools.py` |
| `query_review` | — | 整体平均评分 | `tools/review_tools.py` |
| `query_logistics` | — | 履约指标 | `tools/logistics_tools.py` |
| `query_customer` | — | 复购率指标 | `tools/customer_tools.py` |
| `query_web` | `query` | 联网搜索结果 | `tools/web_search.py` |

模型：`GLM-4.5-Air`（`zhipuai` SDK），联网搜索使用 `zai` SDK。

### 4.10 系统管理（FR-SYS）

| 需求编号 | 需求描述 | 对应接口 | 页面 |
|----------|----------|----------|------|
| FR-SYS-01 | 用户分页列表 | `GET /api/users?page&page_size` | `Users.vue` |
| FR-SYS-02 | 用户详情 | `GET /api/users/{user_id}` | `Users.vue` |
| FR-SYS-03 | 新建用户（密码哈希后入库） | `POST /api/users` | `Users.vue` |
| FR-SYS-04 | 修改用户密码 | `PUT /api/users/{user_id}` | `Users.vue` |
| FR-SYS-05 | 角色列表 | `GET /api/roles` | `Users.vue` |
| FR-SYS-06 | 为用户分配角色 | `PUT /api/users/{user_id}/roles` | `Users.vue` |
| FR-SYS-07 | 操作日志分页查询 | `GET /api/logs?page&page_size` | `Logs.vue` |

写操作审计覆盖情况：`POST /api/users`、`PUT /api/users/{user_id}/roles`、库存调整三处会写 `operation_log`（见 `api/user.py`、`repositories/inventory.py`）；`PUT /api/users/{user_id}`（改密码）当前未写审计日志，属待补充项。

### 4.11 基础数据接口（内部支撑）

以下 5 个接口为数据层原始数据暴露，**无鉴权、无统一响应包装**，仅作内部/调试支撑，未在前端菜单中提供入口：`GET /api/reviews`（评价原始列表）、`GET /api/order_items`（订单明细原始列表）、`GET /api/payments`（支付原始列表）、`GET /api/translation`（类目翻译映射）、`GET /api/geolocation`（地理坐标原始列表）。健康检查 `GET /healthy` 为公开接口。

### 4.12 接口总量

后端实际注册 **51 条路径**（`/api` 下 50 条 + 公开健康检查 `GET /healthy`），按 HTTP 方法计 **52 个 `/api` 操作**（GET 45 / POST 5 / PUT 2），分布于 16 个 router（`app/main.py`）。

## 5. 非功能性需求

### 5.1 性能（NFR-PERF）

| 编号 | 需求 | 现状 |
|------|------|------|
| NFR-PERF-01 | 大列表必须分页，禁止一次性返回十万级数据 | 已实现（`page` / `page_size`） |
| NFR-PERF-02 | 限制最大 `page_size`，防止拖库 | **未实现**：`deps.page_params` 定义了上限 100，但无任何路由使用；各接口 `page_size` 无上界 |
| NFR-PERF-03 | 高频聚合走缓存 | 已实现（Dashboard / 库存） |
| NFR-PERF-04 | 聚合查询依赖现有索引 | 已实现（见 `06_database_design.md` 索引设计） |

### 5.2 缓存（NFR-CACHE）

| 编号 | 需求 | 现状 |
|------|------|------|
| NFR-CACHE-01 | 缓存命中时不得返回陈旧数据 | 库存调整后主动失效相关 key；Dashboard 为静态历史数据，未做失效（可接受） |
| NFR-CACHE-02 | 缓存不可用时核心功能仍可用 | **未实现**：`core/redis.py` 无异常兜底，Redis 不可用会直接抛错 |

### 5.3 安全（NFR-SEC）

| 编号 | 需求 | 现状 |
|------|------|------|
| NFR-SEC-01 | 受保护接口必须鉴权 | 部分实现（5 个裸接口 + `/api/ai/chat` 未鉴权，详见 `11_security_design.md`） |
| NFR-SEC-02 | 密码只存哈希，不存明文 | 已实现（pwdlib Argon2） |
| NFR-SEC-03 | 关键写操作留审计日志 | 部分实现（改密码未记录；`operation_log` 实测 0 行） |
| NFR-SEC-04 | 密钥通过 `.env` 管理，不入 Git | 已实现（`backend/.env`） |

### 5.4 可用性（NFR-AVAIL）

| 编号 | 需求 | 现状 |
|------|------|------|
| NFR-AVAIL-01 | AI 关闭时订单/Dashboard/库存等功能必须正常运行 | 架构上满足（AI 为独立路由与模块） |
| NFR-AVAIL-02 | 统一异常处理（参数错误、未登录、无权限、资源不存在、数据库异常、AI 异常） | 部分实现：已处理 `HTTPException`、`RequestValidationError`；缺未捕获异常兜底（`Exception` handler）与结构化日志 |
| NFR-AVAIL-03 | 前端表格具备 loading / empty / error 状态 | 已实现（Element Plus 表格 + 响应拦截器统一提示） |

### 5.5 AI 质量（NFR-AI）

| 编号 | 需求 | 现状 |
|------|------|------|
| NFR-AI-01 | 事实必须来自工具返回，禁止编造 | 已通过 `SYSTEM_PROMPT` 约束（属提示层约束，非强制校验） |
| NFR-AI-02 | 必须标注数据时间范围与来源 | 已通过 `SYSTEM_PROMPT` 约束 |
| NFR-AI-03 | AI 调用失败应有降级提示 | **未实现**：`services/AI.py` 无 try/except，上游异常将直接冒泡 |

### 5.6 可维护性（NFR-MAINT）

| 编号 | 需求 | 现状 |
|------|------|------|
| NFR-MAINT-01 | 分层：Router → Schema → Service → Repository → DB | 已实现（部分简单查询在 api 层直接调 repository） |
| NFR-MAINT-02 | 统一响应格式 `{code, message, data}` | 部分实现（8 个接口未包装） |
| NFR-MAINT-03 | 依赖可复现 | 已实现：`requirements.txt` 已包含 `zai-sdk==0.2.3`（`tools/web_search.py` 所需）与 `pytest==9.1.1`；环境变量模板见 `backend/.env.example` |

## 6. 验收标准

依据设计文档第 15 章，并结合实现现状标注验收状态。

| 层级 | 验收内容 | 验收标准 | 状态 |
|------|----------|----------|------|
| 数据 | 清洗、缺失、重复、外键 | 质量规则全部通过 | 已达成（见 `04_data_quality_report.md`） |
| 数据库 | CRUD、约束、索引 | 核心 SQL 正常 | 已达成（见 `06_database_design.md`） |
| API | 登录、分页、筛选、详情 | Swagger/Postman 全部可用 | 已达成 |
| 业务 | 订单、库存、物流 | 关键流程正确 | 已达成 |
| 前端 | 页面、筛选、错误状态 | 可操作无明显阻塞 | 已达成 |
| Redis | 命中/失效 | 数据更新后不出现旧缓存 | 部分达成（库存已失效；Dashboard 无失效策略） |
| AI | 事实、工具、异常 | 不编造，能正确调用工具 | 部分达成（无异常降级） |
| 安全 | 权限、token、配置 | 越权访问被拒绝 | **未完全达成**（5 个接口无鉴权 + AI 无鉴权） |
| 性能 | Dashboard、列表 | 在本地测试数据规模下可接受 | 已达成 |
| 部署 | Docker Compose | 一条命令启动主要服务 | **未达成**（仓库内未见 `docker-compose.yml`） |

### 6.1 重点业务验收案例（设计文档 15.1）

| 编号 | 案例 | 预期 | 状态 |
|------|------|------|------|
| AC-01 | 取消订单不应被错误计入有效销售指标 | 销售额/客单价排除 `canceled` | 已实现 |
| AC-02 | 一个订单多个 item 时销售金额不能重复计算 | 按 `order_items` 行求和而非订单数相乘 | 已实现 |
| AC-03 | 同一 `customer_unique_id` 的多个 `customer_id` 正确归并 | 客户数用 `COUNT(DISTINCT)` | 已实现 |
| AC-04 | 评价文本为空时 AI 文本分析不报错 | 空文本跳过 | 已实现（统计口径为评分平均，不解析文本） |
| AC-05 | 库存调整满足 `after = before + change` | 恒等式成立 | 已实现 |
| AC-06 | 修改库存后相关预警缓存失效 | 调整后 `inventory:warnings` 被删除 | 已实现 |
| AC-07 | AI 询问当前政策时必须联网，不得把 2018 年数据冒充当前信息 | 调用 `query_web` 并区分来源 | 依赖提示词约束，**无程序校验** |

## 7. 需求与实现差异说明

### 7.1 已实现（需求 → 实现可追溯）

认证与 RBAC 三项（登录签发 JWT、`/auth/me` 返回角色、43 处 `require_permission` 接口级权限校验）全部落地；八大业务模块（Dashboard / 订单 / 商品类目 / 客户 / 卖家 / 物流 / 库存 / 系统管理）均有可用接口与前端页面；库存模块 8 项需求全部实现（台账、预警、补货建议、流水、缓存失效与 `after = before + change` 恒等式）；AI 助手 Tool Calling 与联网搜索落地，9 个工具与 `ai_analysis` 留痕可用，前端 AI 回复经 DOMPurify 消毒后渲染。

### 7.2 未实现 / 部分实现

（编号 `RD-xx` 为本文件内标识，与 `07_system_design.md` 第 10 章的架构偏差 `D-xx`、`11_security_design.md` 第 10 章的风险 `R-xx` 各自独立。）

| 编号 | 需求 | 差异 | 影响 |
|------|------|------|------|
| RD-01 | 角色体系 | 设计文档第 14 章写 `admin / operator / viewer`，实际落点为 `admin / operator / warehouse`，**viewer 未落地**，而是新增了 warehouse（仓储岗） | 只读旁观角色的需求无对应实现；warehouse 角色承担库存操作，属需求重排。详见 `11_security_design.md` 第 10 章 |
| RD-02 | 统一响应 | 8 个接口未包装：`/api/auth/login`、`/api/auth/register`、`/api/auth/me`、`/api/reviews`、`/api/order_items`、`/api/payments`、`/api/translation`、`/api/geolocation` | 前端 `request.js` 做了双格式兼容，接口契约不一致 |
| RD-03 | 接口鉴权 | `/api/reviews`、`/api/order_items`、`/api/payments`、`/api/translation`、`/api/geolocation`、`/api/ai/chat` 均无鉴权；`/api/auth/register` 亦公开 | 未登录即可读取业务数据，不符合"越权访问被拒绝"验收标准 |
| RD-04 | 分页上限 | `page_params`（`le=100`）定义后未被引用 | 无法阻止超大 `page_size` 查询 |
| RD-05 | 库存调整操作人 | `operator` 取自请求体 `AdjustInventory.operator`，而非 JWT 当前用户 | 审计可被伪造，无法追溯真实操作人 |
| RD-06 | 操作日志 | `operation_log` 实测 0 行；改密码接口未埋点 | 审计能力名义存在、实际无数据 |
| RD-07 | AI 降级 | 无 try/except 与降级话术；`ai_analysis.user_id` 恒为 `None` | AI 上游故障直接 500；无法按人追溯 AI 使用 |
| RD-08 | 全局异常与日志 | 仅有 `HTTPException` / `RequestValidationError` 两个 handler，无 `Exception` 兜底、无结构化日志、无 `request_id`（统一响应结构里定义了但未产出） | 未捕获异常返回 FastAPI 默认格式，破坏统一契约 |
| RD-09 | CORS | 后端未配置 `CORSMiddleware`，开发期依赖 Vite 代理（`target http://127.0.0.1:8000`） | 独立部署前端时无法跨域调用 |
| RD-10 | Docker | 仓库中未见 `docker-compose.yml` 与 Dockerfile | 部署验收标准未达成 |
| RD-11 | 依赖复现 | ~~`requirements.txt` 未收录 `zai`（`zai-sdk`）~~ 已补入 `zai-sdk==0.2.3` 与 `pytest==9.1.1` | 已闭合；`requirements.txt` 仍含 jupyter 等冗余依赖（`pip freeze` 全量导出所致） |
| RD-12 | 接口命名 | 卖家排行/评价为 `/api/seller/...`（单数），库存调整为 `/api/adjust/{product_id}/`（脱离 `/inventory` 前缀） | 与设计文档第 9 章 `/api/inventory/{product_id}/adjust` 不一致 |

### 7.3 需求编号与设计文档的接口对照差异

设计文档第 9 章仅列出 20 个接口，实际实现 51 条路径（`/api` 下 50 条 + `/healthy`）；其中有 3 处路径与文档不一致：

| 设计文档 | 实际实现 | 说明 |
|----------|----------|------|
| `GET /api/dashboard/sales-trend` | `GET /api/dashboard/trend` | 路径简化 |
| `POST /api/inventory/{product_id}/adjust` | `POST /api/adjust/{product_id}/` | 前缀脱离 inventory 模块 |
| `GET /api/operation-logs` | `GET /api/logs` | 路径简化 |

其余设计文档中提及的接口（`/api/ai/analyze-sales`、`/api/ai/inventory-advice`）**未单独实现**，改由 `/api/ai/chat` 通过 Tool Calling 覆盖同等能力。

### 7.4 待补充

- 角色与权限的**实际绑定关系**（`system_role_permission` 行数据）：仓库内未找到 RBAC 初始化/种子 SQL，矩阵中 operator、warehouse 的权限归属为按前端 `ROLE_MENUS` 反推，需导出数据库实际数据核实。详见 `11_security_design.md` 第 3.3 节。
- 数据导出（Excel/CSV）需求：设计文档第 3.1 章"运营主管"提出导出能力，代码中未见导出接口，**待补充需求评审确认是否需要**。
- AI 配置管理页面：功能树中列出"系统管理 → AI配置"，实际无对应接口与页面，**待补充**。