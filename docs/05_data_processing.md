# 数据处理方案（Data Processing）

> 项目：电商运营管理与智能分析平台
> 对应论文章节：系统设计 / 数据处理
> 实现脚本：`data/scripts/clean_fir.py`、`data/scripts/validate_raw.py`

## 1. 数据处理原则（8 条铁律）

1. **原始数据永不覆盖**：raw / processed / business 三层分离。
2. **ID 一律保持字符串**：哈希 ID 不转整数。
3. **邮编前缀按字符串读取**：保留前导 0，避免地域关联失败。
4. **日期统一 DATETIME**：缺失保留 NULL，不填假日期。
5. **金额统一 DECIMAL(12,2)**：不用 float 存钱。
6. **缺失值按业务语义处理**：时间缺失→NULL；文本缺失→空；类目缺失→unknown；数值缺失→NULL。
7. **地理数据先去重再聚合**：避免地域分析重复计数。
8. **清洗规则可复现**：写入脚本 + 文档。

## 2. 处理流水线

```
data/raw/ (原始 CSV)
   ↓ validate_raw.py  →  data/quality/  (质量报告)
   ↓ clean_fir.py
   ↓ (清洗)
   ↓
MySQL 业务库 (olist_xxx_dataset_clean)
```

## 3. 各表清洗规则

### 3.1 customers（客户表）
- `customer_zip_code_prefix` 按 str 读取（保留前导 0）
- `customer_city` 去除首尾空格
- 无缺失，主键 customer_id 唯一

### 3.2 geolocation（地理表）— 特殊处理
- 按 str 读取邮编（保留前导 0）
- `drop_duplicates()` 去除 261,831 行完全重复
- 按 `geolocation_zip_code_prefix` 分组聚合：
  - lat/lng 取 mean
  - city/state 取众数（mode）
- 结果：100 万行 → 19,015 行（一行一邮编）

### 3.3 orders（订单表）
- `order_id`、`customer_id` 保持 str
- 5 个时间字段转 DATETIME，缺失保留 NULL
- `order_status` 枚举校验（8 种合法值）
- 不 fillna 填假日期

### 3.4 order_items（订单明细表）
- `order_id`、`product_id`、`seller_id` 保持 str
- `shipping_limit_date` 转 DATETIME
- `price`、`freight_value` 转 DECIMAL(12,2)

### 3.5 order_payments（支付表）
- 枚举校验 `payment_type`（5 种合法值），删除越界值
- `payment_value` 转 DECIMAL(12,2)

### 3.6 order_reviews（评价表）
- `drop_duplicates('review_id')` 去重（814 个重复 ID 指向不同订单）
- `review_score` 枚举校验（1~5），删除越界值
- `review_comment_title/message` 缺失保留空（不填）
- 时间字段转 DATETIME

### 3.7 products（产品表）
- `product_category_name` 缺失 610 填 `unknown`
- `product_photos_qty < 0` 的异常行删除
- 字段重命名：`product_name_lenght` → `product_name_length`、`product_description_lenght` → `product_description_length`（原字段名拼写错误）
- 删除原拼写错误列
- 数值字段缺失保留 NULL（不填 0）

### 3.8 sellers（卖家表）
- `seller_zip_code_prefix` 按 str 读取（保留前导 0）
- `seller_city` 去除首尾空格

### 3.9 category_translation（翻译表）
- `encoding='utf-8-sig'` 读取，去除 BOM 头
- 与 products 通过 `product_category_name` 关联

## 4. 清洗前后对比

| 表 | 清洗前 | 清洗后 | 主要变化 |
|----|--------|--------|----------|
| geolocation | 1,000,163 | 19,015 | 去重 + 聚合 |
| order_reviews | 99,224 | 98,410 | review_id 去重 |
| orders | 99,441 | 99,441 | 时间转 DATETIME、保留 NULL |
| products | 32,951 | 32,951 | 类目填 unknown、字段改名 |
| 其余表 | — | — | 类型规范化（DECIMAL/DATETIME/char） |

## 5. 遗留说明

- 当前实现为"清洗后直接 to_sql 入库"，本地 processed CSV 可由导出脚本补充（`data/processed/`）。
- category_translation 与 products 的 JOIN 在查询层进行，不在入库时物化英文列。
