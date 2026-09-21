# 电商运营管理与智能分析平台

基于 Olist Brazilian E-Commerce Public Dataset 的电商运营后台管理系统。面向电商运营人员/管理人员，提供订单、产品/类目、客户、卖家、物流、库存等运营分析能力，并在业务系统之上叠加 LLM AI 运营助手。
数据的来源是:https://www.kaggle.com/datasets/mohimohammd/brazilian-e-commerce-public-dataset-by-olist?select=olist_order_payments_dataset.csv
上面的公开数据集，直接下载zip压缩包然后解压到data文件夹下的raw文件夹内。（2026年9月）

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python + FastAPI + SQLAlchemy 2.x + Pydantic |
| 数据库 | MySQL 8.x |
| 缓存 | Redis |
| 认证 | JWT + RBAC |
| 前端 | Vue 3 + Element Plus + ECharts |
| 数据处理 | Pandas / NumPy |
| AI | LLM API + Tool Calling |
| 部署 | Docker Compose |

## 目录结构

```
project/
├─ backend/          # FastAPI 后端
│  ├─ app/           # api 路由 / services 业务 / repositories 数据访问 / models ORM
│  │                 # schemas 数据模型 / core 安全与缓存 / tools AI 工具
│  ├─ seed_inventory.py    # 库存数据初始化脚本
│  ├─ tests/         # pytest 用例（鉴权/权限/响应体/分页，不依赖 MySQL、Redis）
│  ├─ .env           # 环境变量（不入库，从 .env.example 复制后填值）
│  └─ .env.example   # 环境变量模板（入库）
├─ frontend/         # Vue 3 管理后台（views / api / router / stores / layouts）
├─ data/
│  ├─ raw/           # 原始 CSV（9 张表，不入库）
│  ├─ quality/       # 数据质量报告
│  ├─ scripts/       # validate_raw.py 数据校验 / clean_fir.py 清洗并入库
│  └─ database_create.sql  # 业务表建表 + 建索引 DDL
├─ docs/             # 设计文档 01~13
├─ requirements.txt  # 后端依赖（含 zai-sdk、pytest）
├─ pytest.ini        # pytest 配置
└─ docker/           # 预留目录，Docker 化尚未实现
```

> 与设计文档的差异：`data/processed/` 目录未产出，实际流程为「raw CSV → 清洗直写 MySQL」；`docker-compose.yml` 尚未创建（方案见 `docs/13_deployment.md`）。

## 数据说明

- 数据为 Olist 历史匿名电商数据，订单时间 2016-09 ~ 2018-10。
- 9 张核心表：customers / orders / order_items / order_payments / order_reviews / products / sellers / geolocation / category_translation。
- products 无真实商品名称，系统做"产品/类目运营分析"，非商城详情页。
- 库存为项目自建业务模型（原始数据无库存表）。

## 快速开始

```bash
# 1. 准备环境：MySQL 8（建库 olist）+ Redis，Python 3.10+，Node 18+
#    安装依赖：pip install -r requirements.txt

# 2. 配置后端环境变量（必须最先做：清洗脚本也要读它）
cp backend/.env.example backend/.env   # Windows: Copy-Item backend\.env.example backend\.env
#    然后填入真实值：
#    DATABASE_URL=mysql+pymysql://<用户>:<密码>@<主机>:3306/olist?charset=utf8mb4
#    SECRET_KEY=<随机字符串>
#    REDIS_URL=redis://localhost:6379/0
#    ZHIPU_API_KEY=<智谱开放平台 API Key>

# 3. 建业务表（9 张，脚本内含建表与索引）
mysql -uroot -p olist < data/database_create.sql

# 4. 清洗原始 CSV 并入库（要求 data/raw/ 下已放好 9 个原始 CSV）
python data/scripts/clean_fir.py
python data/scripts/validate_raw.py     # 可选：数据质量校验

# 5. 启动后端（应用层 9 张表会在首次启动时由 SQLAlchemy 自动创建）
cd backend && uvicorn app.main:app --reload        # http://127.0.0.1:8000

# 6. 初始化库存数据（可选，会重建 inventory / inventory_log）
python backend/seed_inventory.py

# 7. 启动前端（开发服务器已配置 /api 代理到 127.0.0.1:8000）
cd frontend && npm install && npm run dev          # http://127.0.0.1:5173

# 8. 运行单元测试（可选，不依赖 MySQL / Redis）
python -m pytest                                   # 35 passed
```

注意事项：

- `backend/.env` 必须存在，否则后端与清洗脚本都无法启动；模板见 `backend/.env.example`。
- `clean_fir.py` 已改为相对路径（按脚本位置推导 `data/raw/`）并从 `backend/.env` 读取连接串，换机器无需改脚本。
- 清洗脚本用 `if_exists='append'` 写入，重复执行会重复插入，重跑前请先 `TRUNCATE` 对应的 9 张 `olist_*_clean` 表。
- 表名统一为 `olist_*_dataset_clean`（business 层）与 `system_*` / `inventory*` / `operation_log` / `ai_analysis`（application 层）。
- 新注册的账号默认没有任何角色，需管理员在「系统用户管理」页分配角色后才能登录，否则会被提示"账号暂无权限"。
- 若后端代码改动后不生效，先确认旧的 8000 端口进程已结束，再重启服务。

## 开发进度

- [x] 数据研究 + 清洗 + 入库 + 索引
- [x] FastAPI 后端 + 核心业务 API + Dashboard（共 51 条路径，`/api` 下 52 个操作）
- [x] 库存模块 + 前端 Vue + Redis 缓存
- [x] AI 助手 + Tool Calling + 联网搜索（智谱 GLM）
- [x] 设计文档 01~13
- [x] 单元测试：`backend/tests/` 下 35 个 pytest 用例（鉴权/权限/响应体/分页），`python -m pytest` 全通过
- [ ] 业务聚合与前端 E2E 测试、CI 流水线（详见 `docs/12_test_report.md` §6）
- [ ] Docker Compose 一键部署（方案见 `docs/13_deployment.md`，尚未落地）
- [ ] 遗留整改：部分接口缺鉴权、月度订单量统计重复计数、缺少「AI 配置」与「角色管理」页面（详见 `docs/12_test_report.md` 缺陷清单）

## 文档

详见 `docs/` 目录：

| 文件 | 内容 |
|------|------|
| 01_requirements.md | 需求说明书 |
| 02_dataset_description.md | 数据集描述 |
| 03_data_dictionary.md | 数据字典 |
| 04_data_quality_report.md | 数据质量报告 |
| 05_data_processing.md | 数据处理说明 |
| 06_database_design.md | 数据库设计（含 ER 图与应用层 DDL） |
| 07_system_design.md | 系统设计（架构与时序） |
| 08_api_design.md | 接口设计 |
| 09_frontend_design.md | 前端设计 |
| 10_ai_design.md | AI 运营助手设计 |
| 11_security_design.md | 安全设计 |
| 12_test_report.md | 测试报告 |
| 13_deployment.md | 部署文档 |
