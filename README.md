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
├─ frontend/         # Vue 3 管理后台
├─ data/
│  ├─ raw/           # 原始 CSV（9 张表）
│  ├─ processed/     # 清洗后 CSV
│  ├─ quality/       # 数据质量报告
│  ├─ scripts/       # validate_raw.py / clean_fir.py / load_database.py
│  └─ database_create.sql  # 建表 + 建索引 DDL
├─ docs/             # 设计文档（需求/数据/数据库/API/AI/测试/部署）
├─ docker/           # Docker 配置
└─ docker-compose.yml
```

## 数据说明

- 数据为 Olist 历史匿名电商数据，订单时间 2016-09 ~ 2018-10。
- 9 张核心表：customers / orders / order_items / order_payments / order_reviews / products / sellers / geolocation / category_translation。
- products 无真实商品名称，系统做"产品/类目运营分析"，非商城详情页。
- 库存为项目自建业务模型（原始数据无库存表）。

## 快速开始

```bash
# 1. 初始化数据库
mysql -uroot -p < data/database_create.sql

# 2. 数据清洗 + 导入
python data/scripts/clean_fir.py

# 3. 数据质量检查
python data/scripts/validate_raw.py
```

## 开发进度

- [x] 数据研究 + 清洗 + 入库 + 索引
- [ ] FastAPI 后端 + 核心业务 API + Dashboard
- [ ] 库存模块 + 前端 Vue + Redis
- [ ] AI 助手 + Tool Calling + 联网搜索
- [ ] 测试 + Docker 部署

## 文档

详见 `docs/` 目录：需求、数据集描述、数据字典、数据质量报告、数据处理、数据库设计等。
