# 数据库设计（Database Design）

> 项目：电商运营管理与智能分析平台
> 对应论文章节：系统设计
> 建表脚本：`data/database_create.sql`

## 1. 数据库分层

| 层 | 用途 | 表 |
|----|------|----|
| raw | 保留原始导入结果 | （原始 CSV，未建库） |
| business | 供业务 API 查询 | customers / orders / order_items / products / sellers / payments / reviews / geolocation / category_translation |
| application | 项目新增业务能力 | system_user / system_role / system_permission / system_user_role / system_role_permission / inventory / inventory_log / operation_log / ai_analysis |

> 说明：raw 层本次未落库，原始数据以 CSV 形式保留在 `data/raw/`（见第 7 章的偏差说明）。

## 2. 业务表结构

当前已完成 9 张业务表，命名规则 `olist_<表名>_dataset_clean`。

| 表 | 主键 | 关键索引 |
|----|------|----------|
| customers | customer_id | customer_unique_id |
| geolocation | geolocation_zip_code_prefix | — |
| orders | order_id | customer_id、order_purchase_timestamp |
| order_items | (order_id, order_item_id) | product_id、seller_id |
| order_payments | (order_id, payment_sequential) | payment_type |
| order_reviews | review_id | order_id、review_score |
| products | product_id | product_category_name |
| sellers | seller_id | — |
| category_translation | product_category_name | — |

## 3. 字段类型规范

- **ID 类字段**：`char(35)`（哈希字符串，32 位 + 余量）
- **邮编前缀**：`char(5)`（保留前导 0）
- **金额**：`decimal(12,2)`
- **时间**：`datetime`（可空 NULL）
- **州缩写**：`char(2)`
- **城市/类目**：`varchar(40~50)`
- **字符集**：`utf8mb4`

## 4. 索引设计

索引依据实际查询条件，不冗余、不过度：

| 索引 | 服务场景 |
|------|----------|
| customers(customer_unique_id) | 客户归并、复购分析 |
| orders(customer_id) | 客户 → 订单查询 |
| orders(order_purchase_timestamp) | 时间趋势、Dashboard |
| order_items(product_id) | 产品分析 |
| order_items(seller_id) | 卖家分析 |
| order_payments(payment_type) | 支付方式分析 |
| order_reviews(order_id) | 订单 → 评价 |
| order_reviews(review_score) | 满意度统计 |
| products(product_category_name) | 类目分析 |

> 说明：order_items 的 order_id、payments 的 order_id 已被复合主键最左前缀覆盖，不再单独建索引；小表（sellers 3,095 行、geolocation 1.9 万、translation 71）不建；低基数字段（order_status）不建。

### 4.1 与设计总纲 7.3「索引重点」的对账

设计总纲第 7 章 **7.3 索引重点** 逐字点名了 7 组索引，逐条对账如下：

| 总纲点名 | 实现情况 | 说明 |
|----------|----------|------|
| `orders(customer_id, purchase_at, order_status)` | 已建 `orders(customer_id)` + `orders(order_purchase_timestamp)` | 总纲字段名 `purchase_at`、`order_status` 与实现不一致；实现为两列独立索引，未建复合索引。`order_status` 为低基数（8 个枚举值），单独建索引无收益 |
| `order_items(order_id, product_id, seller_id)` | 已建 `order_items(product_id)` + `order_items(seller_id)`；`order_id` 由主键最左前缀覆盖 | 相符 |
| `payments(order_id, payment_type)` | 已建 `order_payments(payment_type)`；`order_id` 由主键最左前缀覆盖 | 相符 |
| `reviews(order_id, review_score)` | 已建 `order_reviews(order_id)` + `order_reviews(review_score)` | 相符 |
| `products(category_id)` | 已建 `products(product_category_name)` | 总纲字段名为 `category_id`，实际列名为 `product_category_name` |
| `inventory(product_id)` | **无需新建** | 实测 `inventory` 表主键即为 `product_id`（`PRIMARY(product_id)`），总纲要求已被主键满足 |
| `operation_log(user_id, created_at)` | **未建，且无法直接建** | 实测 `operation_log` **没有 `user_id` 列**（只有 `operator varchar(50)` 存用户名）；当前查询只按 `ORDER BY id DESC` 分页，主键已够用。总纲要求与实现的数据模型不一致，属设计偏差而非遗漏 |

总纲 7.3 的收尾原则是「不要为了'看起来专业'给每个字段都建索引，索引依据实际查询条件和 `EXPLAIN` 结果逐步增加」。按此原则，应用层唯一有实际收益的候选是 `inventory_log(product_id, created_at)`（实测 65,905 行，`get_inventory_logs` 对 `WHERE product_id = ?` 做分页 + `COUNT`，当前只有主键，属全表扫描）——列入待办，本轮不执行。

## 5. ER 图（Mermaid）

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : "places"
    ORDERS ||--o{ ORDER_ITEMS : "contains"
    ORDERS ||--o{ PAYMENTS : "paid_by"
    ORDERS ||--o{ REVIEWS : "has"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered_as"
    SELLERS ||--o{ ORDER_ITEMS : "sells"
    PRODUCTS }o--|| CATEGORY_TRANSLATION : "translated_by"
    CUSTOMERS }o--o{ GEOLOCATION : "located_via_zip"
    SELLERS }o--o{ GEOLOCATION : "located_via_zip"

    CUSTOMERS {
        char customer_id PK
        char customer_unique_id
        char customer_zip_code_prefix
        varchar customer_city
        char customer_state
    }

    ORDERS {
        char order_id PK
        char customer_id FK
        char order_status
        datetime order_purchase_timestamp
        datetime order_approved_at
        datetime order_delivered_carrier_date
        datetime order_delivered_customer_date
        datetime order_estimated_delivery_date
    }

    ORDER_ITEMS {
        char order_id PK
        int order_item_id PK
        char product_id FK
        char seller_id FK
        datetime shipping_limit_date
        decimal price
        decimal freight_value
    }

    PRODUCTS {
        char product_id PK
        varchar product_category_name
        int product_name_length
        int product_description_length
        tinyint product_photos_qty
        int product_weight_g
        int product_length_cm
        int product_height_cm
        int product_width_cm
    }

    SELLERS {
        char seller_id PK
        char seller_zip_code_prefix
        varchar seller_city
        char seller_state
    }

    PAYMENTS {
        char order_id PK
        int payment_sequential PK
        varchar payment_type
        int payment_installments
        decimal payment_value
    }

    REVIEWS {
        char review_id PK
        char order_id FK
        int review_score
        varchar review_comment_title
        varchar review_comment_message
        datetime review_creation_date
        datetime review_answer_timestamp
    }

    CATEGORY_TRANSLATION {
        varchar product_category_name PK
        varchar product_category_name_english
    }

    GEOLOCATION {
        char geolocation_zip_code_prefix PK
        double geolocation_lat
        double geolocation_lng
        varchar geolocation_city
        char geolocation_state
    }
```

> 渲染方式：将上面代码块复制到 mermaid.live、Typora、或 VS Code（安装 Mermaid 插件）即可生成 ER 图，导出 PNG 放到 `docs/figures/er_diagram.png`。

## 6. 应用层表结构（DDL）

以下 DDL 与线上数据库（MySQL 8.0，utf8mb4）**逐字一致**，可用 `SHOW CREATE TABLE <表名>` 复核。

### 6.1 系统用户与 RBAC

```sql
CREATE TABLE `system_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `system_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `system_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `system_user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `system_user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `system_user` (`id`),
  CONSTRAINT `system_user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `system_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `system_role_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `system_role_permission_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `system_role` (`id`),
  CONSTRAINT `system_role_permission_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `system_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

用户 → 角色 → 权限为多对多两级关联：鉴权时由 `system_user_role` 找到角色，再由 `system_role_permission` 汇总该用户的权限集合（实现见 `backend/app/repositories/permission.py`）。

### 6.2 库存

```sql
CREATE TABLE `inventory` (
  `product_id` varchar(35) NOT NULL,
  `quantity` int NOT NULL,
  `safety_stock` int NOT NULL,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `inventory_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` varchar(35) NOT NULL,
  `change` int NOT NULL,
  `before` int NOT NULL,
  `after` int NOT NULL,
  `reason` varchar(100) DEFAULT NULL,
  `operator` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

`safety_stock` 为预警阈值，`quantity` 为当前库存；`inventory_log` 记录每次调整的前后值，满足 `after = before + change` 的约束（由服务层保证，见 `backend/app/services/inventory.py`）。

### 6.3 审计与 AI 记录

```sql
CREATE TABLE `operation_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `operator` varchar(50) NOT NULL,
  `action` varchar(50) NOT NULL,
  `target` varchar(100) DEFAULT NULL,
  `detail` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ai_analysis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) DEFAULT NULL,
  `question` text NOT NULL,
  `tool_context` text,
  `answer` text NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

## 7. 应用层索引与已知缺口

| 项 | 现状 | 影响 / 建议 |
|----|------|-------------|
| `inventory_log` 索引 | 仅有主键（65,905 行） | **待办（本轮未执行）**：`get_inventory_logs` 对 `WHERE product_id = ?` 做分页 + `COUNT`，属全表扫描；建议加 `KEY (product_id, created_at)`。总纲 7.3 未点名该表，属"依据实际查询条件"的合理延伸，见 §4.1 |
| `operation_log` 索引 | 仅有主键（实测 0 行） | **不加**：总纲 7.3 点名 `operation_log(user_id, created_at)`，但该表**无 `user_id` 列**（只有 `operator`），且查询只按 `ORDER BY id DESC` 分页，主键已覆盖；表当前 0 行也无需优化。见 §4.1 |
| `inventory` 外键 | 无 `product_id` 外键 | 库存是项目自建模型，允许对任意商品建档，故不加外键，属有意设计 |
| `system_user` 字段 | 无 `status`、无 `created_at` | 无法禁用账号、无法记录注册时间；如需"停用用户"功能需补列 |
| `ai_analysis.user_id` | 实测记录全部为 NULL | 未关联提问用户，建议由服务层写入当前登录用户 |
| 建表脚本 | `data/database_create.sql` **只含 9 张业务表**（DDL 见本文件第 6 节） | 剩余 9 张应用表由后端启动时 `app/main.py` 末尾的 `Base.metadata.create_all(bind=engine)` 创建。**已决策维持现状**：单机单实例项目里 `create_all` 在启动时幂等建表，`database_create.sql` 只需负责 9 张业务表 + 索引，无需再追加一份应用层 DDL 造成两处定义漂移 |
| raw 层 | 未落库 | 原始数据以 CSV 保存在 `data/raw/`，`data/processed/` 目录未产出，实际为"raw CSV → 清洗直写 MySQL"两步流程 |
| 迁移工具 | 未引入 Alembic | **已决策暂不引入**：当前是单机开发、表结构只在开发期变动，`create_all` + 手工改表足够；引入 Alembic 需要维护 version 目录与迁移链，收益不足（后续若需多环境部署再补） |
