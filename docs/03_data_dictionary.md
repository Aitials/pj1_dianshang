# 数据字典（Data Dictionary）

> 项目：电商运营管理与智能分析平台
> 对应论文章节：相关数据与需求分析
> 说明：字段类型为清洗后入库（MySQL）的类型；"清洗处理"列说明从原始到入库做了哪些转换。

---

## 1. customers（客户表）— 99,441 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| customer_id | char(35) PK | 客户记录 ID（订单关联键） | 保持字符串，不转整数 |
| customer_unique_id | char(35) | 真实客户唯一 ID（归并用） | 保持字符串，建有索引 |
| customer_zip_code_prefix | char(5) | 客户邮编前缀 | 按字符串读取，保留前导 0 |
| customer_city | varchar(40) | 城市 | 去除首尾空格 |
| customer_state | char(2) | 州（巴西州缩写） | 保持 |

## 2. geolocation（地理表）— 聚合后 19,015 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| geolocation_zip_code_prefix | char(5) PK | 邮编前缀 | 去重后按邮编聚合，保留前导 0 |
| geolocation_lat | double | 纬度 | 同一邮编取平均 |
| geolocation_lng | double | 经度 | 同一邮编取平均 |
| geolocation_city | varchar(50) | 城市 | 取众数 |
| geolocation_state | char(2) | 州 | 取众数 |

> 原始 100 万行 → 去重（约 26 万完全重复）→ 按邮编聚合 → 19,015 行（一行一邮编）。

## 3. orders（订单表）— 99,441 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| order_id | char(35) PK | 订单唯一 ID | 保持字符串 |
| customer_id | char(35) | 下单客户 ID | 保持字符串，建有索引 |
| order_status | char(15) | 订单状态（8 种枚举） | 枚举校验 |
| order_purchase_timestamp | datetime | 下单时间 | 转 DATETIME，趋势分析基准 |
| order_approved_at | datetime | 审核通过时间 | 转 DATETIME，缺失 160 保留 NULL |
| order_delivered_carrier_date | datetime | 交给承运商时间 | 转 DATETIME，缺失 1,783 保留 NULL |
| order_delivered_customer_date | datetime | 实际送达时间 | 转 DATETIME，缺失 2,965 保留 NULL |
| order_estimated_delivery_date | datetime | 预计送达时间 | 转 DATETIME，用于算准时率 |

**order_status 枚举值**：delivered / shipped / canceled / unavailable / invoiced / processing / created / approved

## 4. order_items（订单明细表）— 112,650 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| order_id | char(35) PK | 所属订单 ID | 保持字符串 |
| order_item_id | int PK | 订单内商品序号（从 1 起） | 保持整数 |
| product_id | char(35) | 商品 ID | 保持字符串，建有索引 |
| seller_id | char(35) | 卖家 ID | 保持字符串，建有索引 |
| shipping_limit_date | datetime | 卖家发货截止时间 | 转 DATETIME |
| price | decimal(12,2) | 商品单价 | 金额转 DECIMAL |
| freight_value | decimal(12,2) | 运费 | 金额转 DECIMAL |

> 主键为 (order_id, order_item_id) 复合主键。销售额 = price 求和（需排除取消订单）。

## 5. order_payments（支付表）— 103,886 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| order_id | char(35) PK | 订单 ID | 保持字符串 |
| payment_sequential | int PK | 支付序号（一个订单可多笔） | 保持整数 |
| payment_type | varchar(15) | 支付方式 | 枚举校验，建有索引 |
| payment_installments | int | 分期数 | 保持整数 |
| payment_value | decimal(12,2) | 该笔支付金额 | 金额转 DECIMAL |

**payment_type 枚举值**：credit_card / boleto / voucher / debit_card / not_defined
> 主键为 (order_id, payment_sequential) 复合主键。

## 6. order_reviews（评价表）— 清洗后 98,410 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| review_id | char(35) PK | 评价唯一 ID | 去重（814 个重复 ID） |
| order_id | char(35) | 关联订单 | 保持字符串，建有索引 |
| review_score | int | 评分 1~5 | 枚举校验，建有索引 |
| review_comment_title | varchar(50) | 评价标题 | 缺失 87,656 保留空 |
| review_comment_message | varchar(500) | 评价正文 | 缺失 58,247 保留空 |
| review_creation_date | datetime | 评价创建时间 | 转 DATETIME |
| review_answer_timestamp | datetime | 商家回复时间 | 转 DATETIME |

## 7. products（产品表）— 32,951 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| product_id | char(35) PK | 商品 ID | 保持字符串 |
| product_category_name | varchar(50) | 商品类目（葡语） | 缺失 610 填 unknown，建有索引 |
| product_name_length | int | 商品名称长度 | 原字段名 lenght（拼写错误）已改名 |
| product_description_length | int | 描述长度 | 原字段名 lenght 已改名 |
| product_photos_qty | tinyint | 照片数量 | 保持 |
| product_weight_g | int | 重量（克） | 保持 |
| product_length_cm | int | 长（厘米） | 保持 |
| product_height_cm | int | 高（厘米） | 保持 |
| product_width_cm | int | 宽（厘米） | 保持 |

> 注意：本表**无真实商品名称**，只有属性字段。

## 8. sellers（卖家表）— 3,095 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| seller_id | char(35) PK | 卖家 ID | 保持字符串 |
| seller_zip_code_prefix | char(5) | 卖家邮编前缀 | 按字符串读取，保留前导 0 |
| seller_city | varchar(50) | 卖家城市 | 去除首尾空格 |
| seller_state | char(2) | 卖家州 | 保持 |

## 9. product_category_name_translation（类目翻译表）— 71 行

| 字段 | 类型 | 含义 | 清洗处理 |
|------|------|------|----------|
| product_category_name | varchar(50) PK | 类目名（葡语） | 用 utf-8-sig 读取去除 BOM |
| product_category_name_english | varchar(50) | 类目名（英语） | 保持 |
