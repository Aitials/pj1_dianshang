# 数据质量报告（Data Quality Report）

> 项目：电商运营管理与智能分析平台
> 对应论文章节：系统设计 / 数据处理
> 生成方式：由 `data/scripts/validate_raw.py` 自动统计，非人工估算。

## 1. 总览

| 文件 | 行数 | 字段数 | 缺失单元格 | 完全重复行 |
|------|------|--------|------------|------------|
| olist_customers_dataset.csv | 99,441 | 5 | 0 | 0 |
| olist_geolocation_dataset.csv | 1,000,163 | 5 | 0 | 261,831 |
| olist_order_items_dataset.csv | 112,650 | 7 | 0 | 0 |
| olist_order_payments_dataset.csv | 103,886 | 5 | 0 | 0 |
| olist_order_reviews_dataset.csv | 99,224 | 7 | 145,903 | 0 |
| olist_orders_dataset.csv | 99,441 | 8 | 4,908 | 0 |
| olist_products_dataset.csv | 32,951 | 9 | 2,448 | 0 |
| olist_sellers_dataset.csv | 3,095 | 4 | 0 | 0 |
| product_category_name_translation.csv | 71 | 2 | 0 | 0 |

## 2. 缺失值明细

| 表 | 字段 | 缺失数 | 处理方式 |
|----|------|--------|----------|
| order_reviews | review_comment_title | 87,656 | 保留空，不填 |
| order_reviews | review_comment_message | 58,247 | 保留空，不填 |
| orders | order_approved_at | 160 | 保留 NULL |
| orders | order_delivered_carrier_date | 1,783 | 保留 NULL |
| orders | order_delivered_customer_date | 2,965 | 保留 NULL |
| products | product_category_name | 610 | 填 unknown |
| products | product_name_lenght | 610 | 保留 NULL |
| products | product_description_lenght | 610 | 保留 NULL |
| products | product_photos_qty | 610 | 保留 NULL |
| products | product_weight_g | 2 | 保留 NULL |
| products | product_length_cm | 2 | 保留 NULL |
| products | product_height_cm | 2 | 保留 NULL |
| products | product_width_cm | 2 | 保留 NULL |

> 关键发现：products 有 610 行同时缺失"类目/名称长度/描述长度/照片数量"，判断为同一批异常记录；重量/尺寸仅 2 行缺失。

## 3. 重复值分析

| 表 | 检查对象 | 结果 |
|----|----------|------|
| geolocation | 整行 | 261,831 行完全重复 |
| order_reviews | review_id | 98410 唯一，814 重复（指向不同订单） |
| 其余表 | 主键 | 0 重复 |

**处理决策**：
- geolocation：先去重，再按邮编聚合经纬度 → 19,015 行。
- order_reviews：review_id 存在 789 个重复 ID（对应 814 行），均指向不同 order_id，按 review_id 去重保留首条 → 98,410 行。

## 4. 主键唯一性

| 表 | 主键 | 唯一值数 | 重复数 | 结论 |
|----|------|---------|--------|------|
| customers | customer_id | 99,441 | 0 | ✅ |
| geolocation | zip_prefix | 19,015 | 981,148 | ⚠️ 需聚合 |
| order_items | (order_id, order_item_id) | 112,650 | 0 | ✅ |
| order_payments | (order_id, payment_sequential) | 103,886 | 0 | ✅ |
| order_reviews | review_id | 98,410 | 814 | ⚠️ 去重 |
| orders | order_id | 99,441 | 0 | ✅ |
| products | product_id | 32,951 | 0 | ✅ |
| sellers | seller_id | 3,095 | 0 | ✅ |
| translation | product_category_name | 71 | 0 | ✅ |

## 5. 枚举值检查

### order_status（订单状态）
| 值 | 数量 |
|----|------|
| delivered | 96,478 |
| shipped | 1,107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

### payment_type（支付方式）
| 值 | 数量 |
|----|------|
| credit_card | 76,795 |
| boleto | 19,784 |
| voucher | 5,775 |
| debit_card | 1,529 |
| not_defined | 3 |

### review_score（评分）
| 值 | 数量 |
|----|------|
| 5 | 57,328 |
| 4 | 19,142 |
| 3 | 8,179 |
| 2 | 3,151 |
| 1 | 11,424 |

> 结论：枚举值均在合法范围内，无越界异常。评分呈"5 分最多"的典型电商好评分布。

## 6. 时间范围

| 字段 | 最小值 | 最大值 | 缺失 |
|------|--------|--------|------|
| order_purchase_timestamp | 2016-09-04 | 2018-10-17 | 0 |
| order_approved_at | 2016-09-15 | 2018-09-03 | 160 |
| order_delivered_carrier_date | 2016-10-08 | 2018-09-11 | 1,783 |
| order_delivered_customer_date | 2016-10-11 | 2018-10-17 | 2,965 |
| order_estimated_delivery_date | 2016-09-30 | 2018-11-12 | 0 |

## 7. 质量结论

1. 数据整体质量良好，主键唯一性高（除 geolocation、reviews 外）。
2. 主要质量问题：geolocation 重复、reviews 文本缺失、orders 时间缺失、products 类目缺失。
3. 所有问题均已在数据清洗阶段按业务语义处理，处理规则见 `05_data_processing.md`。
