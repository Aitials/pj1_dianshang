# 电商运营管理与智能分析平台

基于 Olist 巴西电商公开数据集的电商运营后台管理系统。系统面向电商运营人员与管理者，提供仪表盘、订单、商品/类目、客户、卖家、物流、库存等模块的运营分析能力，并内置基于大语言模型的 AI 运营助手，支持用自然语言查询业务数据、生成分析结论与联网检索外部信息。

## 功能特性

- **数据看板**：GMV、订单量、客单价、趋势曲线与热门类目排行等核心指标。
- **订单管理**：订单列表与详情、订单状态、支付方式、评分评价、运费与配送信息。
- **商品与类目分析**：销量、销售额、类目分布与商品维度下钻。
- **客户与卖家分析**：客户地域分布、消费排行，卖家履约表现。
- **物流分析**：配送时长、延迟率、运费占比等指标。
- **库存管理**：自建库存模型，含库存列表、库存预警与出入库流水。
- **AI 运营助手**：基于 Tool Calling 自动调用业务工具回答运营问题，可联网搜索实时信息，具备多轮会话记忆。
- **认证与审计**：JWT 登录认证、RBAC 角色权限控制、操作日志与 AI 问答记录留痕。
- **查询缓存**：Redis 缓存总览、趋势、排行等热点查询。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.14 + FastAPI + SQLAlchemy 2.x + Pydantic v2 |
| 数据库 | MySQL 8.x（业务数据）、PostgreSQL（AI 会话记忆持久化） |
| 缓存 | Redis |
| 认证 | JWT（python-jose）+ RBAC + Argon2 |
| 前端 | Vue 3 + Vite + Element Plus + ECharts + Pinia + Vue Router |
| 数据处理 | Pandas / NumPy |
| AI | LangChain 1.x `create_agent` + LangGraph + 智谱 GLM-4.5-Air（Tool Calling、联网搜索） |
| 部署 | Docker Compose + Nginx |

## 系统架构

```mermaid
flowchart LR
    U[浏览器] --> F["Vue 3 前端<br/>Vite Dev Server / Nginx"]
    F -->|/api| B["FastAPI 后端<br/>app.main:app"]
    B --> M[("MySQL 8<br/>业务数据")]
    B --> R[("Redis<br/>查询缓存")]
    B --> P[("PostgreSQL<br/>Agent 会话记忆")]
    B -->|HTTP| G["智谱 GLM-4.5-Air<br/>Chat / Web Search"]
    B --> T["本地业务工具<br/>订单 / 商品 / 库存 / 物流 / 客户 / 评价"]
```

## 目录结构

```
pj1_dianshang/
├─ backend/
│  ├─ app/
│  │  ├─ api/            # 路由层：认证、订单、商品、客户、卖家、物流、库存、看板、AI 等
│  │  ├─ core/           # 安全（JWT / Argon2）、统一响应体、Redis 客户端
│  │  ├─ db/             # 数据库引擎与 Session
│  │  ├─ models/         # SQLAlchemy ORM 模型
│  │  ├─ repositories/   # 数据访问层
│  │  ├─ schemas/        # Pydantic 出入参模型
│  │  ├─ services/       # 业务编排；AI.py 为 LangChain Agent
│  │  ├─ tools/          # Agent 工具：看板 / 订单 / 库存 / 评价 / 物流 / 客户 / 联网搜索
│  │  └─ main.py         # 应用装配、全局异常处理、路由挂载
│  ├─ tests/             # pytest 用例
│  ├─ seed_inventory.py  # 库存数据初始化脚本
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  │  ├─ api/            # 接口封装（axios）
│  │  ├─ layouts/        # 页面布局
│  │  ├─ router/         # 路由表
│  │  ├─ stores/         # Pinia 状态
│  │  ├─ utils/          # 请求封装、AI 会话本地存储
│  │  └─ views/          # 页面组件
│  ├─ nginx.conf         # 容器内托管静态资源并反代 /api
│  └─ Dockerfile
├─ data/
│  ├─ raw/               # 原始 CSV（9 张表，需自行下载放入）
│  ├─ quality/           # 数据质量报告
│  ├─ scripts/           # validate_raw.py 数据校验 / clean_fir.py 清洗并入库
│  └─ database_create.sql # 建库 + 18 张表 + 索引 + RBAC 初始数据
├─ docs/                 # 设计文档 01~13
├─ docker-compose.yml    # MySQL + Redis + 后端 + Nginx 前端 + 数据初始化服务
├─ requirements.txt
├─ pytest.ini
├─ .env.example          # 环境变量模板
└─ .env                  # 环境变量实值（不入库）
```

## 快速开始

### 前置要求

- Python 3.10+（项目在 3.14 上开发）
- Node.js 18+
- MySQL 8.x、Redis、PostgreSQL
- 智谱开放平台 API Key（<https://open.bigmodel.cn/>）

### 数据准备

从 Kaggle 下载数据集：<https://www.kaggle.com/datasets/mohimohammd/brazilian-e-commerce-public-dataset-by-olist>

解压后把 9 个 CSV 放到 `data/raw/` 目录下。

### 方式一：Docker Compose（推荐）

```bash
# 1. 准备配置与数据
cp .env.example .env          # Windows: Copy-Item .env.example .env，然后填入真实值

# 2. 启动 MySQL 与 Redis
#    首次初始化会自动执行 data/database_create.sql：建库 + 18 张表 + 索引 + RBAC 初始数据
docker compose up -d mysql redis

# 3. 导入 Olist 业务数据与库存数据（仅需执行一次）
docker compose --profile init run --rm loader

# 4. 启动全部服务
docker compose up -d
```

完成后访问 <http://localhost:8080>，初始管理员账号为 `admin`（密码见 `data/database_create.sql` 文件头，登录后请立即修改）。

端口映射：前端 `8080`、后端 `8000`、MySQL `3307 → 3306`、Redis `6380 → 6379`（映射到非默认端口以避开宿主机已占用的 3306/6379）。

重置数据库：`docker compose down -v`，之后重新执行第 2~4 步。

### 方式二：本地开发

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 配置环境变量（必做，清洗脚本与后端都依赖它）
cp .env.example .env          # Windows: Copy-Item .env.example .env

# 3. 初始化数据库（建库 + 18 张表 + 索引）
mysql -uroot -p olist < data/database_create.sql

# 4. 清洗原始 CSV 并入库（需 data/raw/ 下已放好 9 个 CSV）
python data/scripts/clean_fir.py
python data/scripts/validate_raw.py     # 可选：生成数据质量报告

# 5. 启动后端
cd backend && uvicorn app.main:app --reload     # http://127.0.0.1:8000

# 6. 初始化库存数据（可选，会重建 inventory / inventory_log）
python backend/seed_inventory.py

# 7. 启动前端（开发服务器已配置 /api 代理到 127.0.0.1:8000）
cd frontend && npm install && npm run dev       # http://127.0.0.1:5173
```

运行单元测试（不依赖 MySQL / Redis）：

```bash
python -m pytest
```

## 环境变量

变量集中放在仓库根目录的 `.env`（从 `.env.example` 复制），后端与数据脚本均读取该文件：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | MySQL 连接串，如 `mysql+pymysql://user:pass@host:3306/olist?charset=utf8mb4` |
| `SECRET_KEY` | JWT HS256 签名密钥，建议不少于 32 字节 |
| `REDIS_URL` | Redis 连接串，如 `redis://localhost:6379/0` |
| `ZHIPU_API_KEY` | 智谱开放平台 API Key |
| `ZHIPU_BASE_URL` | 智谱 OpenAI 兼容端点，默认 `https://open.bigmodel.cn/api/paas/v4/` |
| `AGENT_DB_URL` | PostgreSQL 连接串，用于持久化 AI 会话记忆 |

## API 概览

所有接口以 `/api` 为前缀，返回统一响应体 `{ code, message, data }`。

| 模块 | 说明 |
|------|------|
| 认证 `/api/auth` | 登录、令牌签发与当前用户信息 |
| 看板 `/api/dashboard` | 总览指标、趋势与排行 |
| 订单 | 订单列表与详情、订单明细、支付、评价 |
| 商品 | 商品列表与详情、类目及类目翻译 |
| 客户 / 卖家 | 列表、详情与地域分布 |
| 物流 | 配送时效与运费分析 |
| 库存 | 库存列表、库存预警与出入库流水 |
| 系统 | 用户、角色权限、操作日志 |
| AI `/api/ai` | 运营助手问答与会话管理 |
| 健康检查 `/healthy` | 服务健康探针 |

完整接口清单见 `docs/08_api_design.md`。

## 注意事项

- `.env` 必须存在，否则后端与数据清洗脚本都无法启动。
- AI 模块在导入期即初始化智谱客户端与 PostgreSQL 连接，缺少 `ZHIPU_API_KEY` 或 `AGENT_DB_URL` 会导致后端进程启动失败。
- Docker 部署时若 `AGENT_DB_URL` 指向宿主机上的 PostgreSQL，容器内需写 `host.docker.internal` 而非 `localhost`。
- `clean_fir.py` 以 `append` 方式写入，重复执行会重复插入数据；重跑前请先清空对应的 9 张 `olist_*_dataset_clean` 表。
- 数据库表命名：业务层为 `olist_*_dataset_clean`，应用层为 `system_*` / `inventory*` / `operation_log` / `ai_analysis`。
- 新注册账号默认不带任何角色，需管理员在「系统用户管理」中分配角色后才能正常使用。
- 若后端代码改动后未生效，请先确认旧的 8000 端口进程已结束再重启服务。

## 文档

| 文件 | 内容 |
|------|------|
| docs/01_requirements.md | 需求说明书 |
| docs/02_dataset_description.md | 数据集描述 |
| docs/03_data_dictionary.md | 数据字典 |
| docs/04_data_quality_report.md | 数据质量报告 |
| docs/05_data_processing.md | 数据处理说明 |
| docs/06_database_design.md | 数据库设计（含 ER 图与应用层 DDL） |
| docs/07_system_design.md | 系统设计（架构与时序） |
| docs/08_api_design.md | 接口设计 |
| docs/09_frontend_design.md | 前端设计 |
| docs/10_ai_design.md | AI 运营助手设计 |
| docs/11_security_design.md | 安全设计 |
| docs/12_test_report.md | 测试报告 |
| docs/13_deployment.md | 部署文档 |
