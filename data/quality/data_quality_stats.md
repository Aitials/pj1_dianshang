# 原始数据质量统计报告

> 由 validate_raw.py 自动生成

| 文件 | 行数 | 字段数 | 缺失单元格 | 完全重复行 |
|------|------|--------|------------|------------|
| olist_customers_dataset.csv | 99441 | 5 | 0 | 0 |
| olist_geolocation_dataset.csv | 1000163 | 5 | 0 | 261831 |
| olist_order_items_dataset.csv | 112650 | 7 | 0 | 0 |
| olist_order_payments_dataset.csv | 103886 | 5 | 0 | 0 |
| olist_order_reviews_dataset.csv | 99224 | 7 | 145903 | 0 |
| olist_orders_dataset.csv | 99441 | 8 | 4908 | 0 |
| olist_products_dataset.csv | 32951 | 9 | 2448 | 0 |
| olist_sellers_dataset.csv | 3095 | 4 | 0 | 0 |
| product_category_name_translation.csv | 71 | 2 | 0 | 0 |

## 枚举值分布

### olist_orders_dataset.csv :: order_status
- delivered: 96478
- shipped: 1107
- canceled: 625
- unavailable: 609
- invoiced: 314
- processing: 301
- created: 5
- approved: 2

### olist_order_payments_dataset.csv :: payment_type
- credit_card: 76795
- boleto: 19784
- voucher: 5775
- debit_card: 1529
- not_defined: 3

### olist_order_reviews_dataset.csv :: review_score
- 5: 57328
- 4: 19142
- 1: 11424
- 3: 8179
- 2: 3151

## 主键唯一性检查
- olist_customers_dataset.csv 主键 ['customer_id']: 总行 99441，唯一 99441，重复 0
- olist_geolocation_dataset.csv 主键 ['geolocation_zip_code_prefix']: 总行 1000163，唯一 19015，重复 981148
- olist_order_items_dataset.csv 主键 ['order_id', 'order_item_id']: 总行 112650，唯一 112650，重复 0
- olist_order_payments_dataset.csv 主键 ['order_id', 'payment_sequential']: 总行 103886，唯一 103886，重复 0
- olist_order_reviews_dataset.csv 主键 ['review_id']: 总行 99224，唯一 98410，重复 814
- olist_orders_dataset.csv 主键 ['order_id']: 总行 99441，唯一 99441，重复 0
- olist_products_dataset.csv 主键 ['product_id']: 总行 32951，唯一 32951，重复 0
- olist_sellers_dataset.csv 主键 ['seller_id']: 总行 3095，唯一 3095，重复 0
- product_category_name_translation.csv 主键 ['product_category_name']: 总行 71，唯一 71，重复 0

## 时间字段范围
- olist_orders_dataset.csv :: order_purchase_timestamp: min=2016-09-04 21:15:19 max=2018-10-17 17:30:18 缺失=0
- olist_orders_dataset.csv :: order_approved_at: min=2016-09-15 12:16:38 max=2018-09-03 17:40:06 缺失=160
- olist_orders_dataset.csv :: order_delivered_carrier_date: min=2016-10-08 10:34:01 max=2018-09-11 19:48:28 缺失=1783
- olist_orders_dataset.csv :: order_delivered_customer_date: min=2016-10-11 13:46:32 max=2018-10-17 13:22:46 缺失=2965
- olist_orders_dataset.csv :: order_estimated_delivery_date: min=2016-09-30 00:00:00 max=2018-11-12 00:00:00 缺失=0

## 各字段缺失数明细

### olist_customers_dataset.csv

### olist_geolocation_dataset.csv

### olist_order_items_dataset.csv

### olist_order_payments_dataset.csv

### olist_order_reviews_dataset.csv
- review_comment_title: 缺失 87656
- review_comment_message: 缺失 58247

### olist_orders_dataset.csv
- order_approved_at: 缺失 160
- order_delivered_carrier_date: 缺失 1783
- order_delivered_customer_date: 缺失 2965

### olist_products_dataset.csv
- product_category_name: 缺失 610
- product_name_lenght: 缺失 610
- product_description_lenght: 缺失 610
- product_photos_qty: 缺失 610
- product_weight_g: 缺失 2
- product_length_cm: 缺失 2
- product_height_cm: 缺失 2
- product_width_cm: 缺失 2

### olist_sellers_dataset.csv

### product_category_name_translation.csv




## 1. orders（订单表）—— 最核心的事实表

一条记录 = 一笔订单 + 它的完整时间线。**8 个字段，99,441 行**。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `order_id` | 订单唯一 ID | 主键，串联明d细/支付/评价 |
| `customer_id` | 下单客户 ID | 外键 → `customers.customer_id`（注意是"客户记录ID"，不是真实人ID） |
| `order_status` | 订单状态 | 枚举：`delivered`(已送达)、`shipped`(已发货)、`canceled`(取消)、`unavailable`、`invoiced`、`processing`、`created`、`approved` |
| `order_purchase_timestamp` | 下单时间 | **计算趋势、客单价、复购的基准时间**，基本不缺失 |
| `order_approved_at` | 支付审核通过时间 | 缺 160 条，保留 NULL |
| `order_delivered_carrier_date` | 交给承运商时间 | 缺 1783 条，用于算"发货耗时" |
| `order_delivered_customer_date` | 实际送达客户时间 | 缺 2965 条，用于算"履约/延迟" |
| `order_estimated_delivery_date` | 预计送达时间 | 与实际送达对比 → **准时率、延迟率** |

**关键理解**：这张表的核心价值是那条**时间线**（下单→审核→发货→送达→预计送达），物流分析模块几乎全靠它。

---

## 2. order_items（订单商品明细表）—— 销售金额的真正来源

一条记录 = 订单里的**一件商品**。**7 字段，112,650 行**（比订单多，因为一个订单多件商品）。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `order_id` | 所属订单 ID | 外键 → orders |
| `order_item_id` | 该商品在订单内的序号（从 1 开始） | 同一订单多件商品靠它区分 |
| `product_id` | 商品 ID | 外键 → products |
| `seller_id` | 卖家 ID | 外键 → sellers |
| `shipping_limit_date` | 卖家发货截止时间 | 物流分析可用 |
| `price` | 商品单价 | **销售额计算基础** |
| `freight_value` | 运费 | 单独记录，方便拆分"货值 vs 运费" |

**关键理解**：销售额 = `price` 求和（要排除取消订单）。**一个订单有多个 item 时，金额不能重复计算**——这是文档里点名的测试用例。

---

## 3. order_payments（支付表）

一条记录 = 一笔支付。**5 字段，103,886 行**。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `order_id` | 订单 ID | 外键 → orders |
| `payment_sequential` | 支付序号 | 一个订单可能**分多笔支付**（1、2、3…），统计订单实付金额要按 order 求和 |
| `payment_type` | 支付方式 | `credit_card`(信用卡)、`boleto`(银行单)、`voucher`(券)、`debit_card`(借记卡)、`not_defined` |
| `payment_installments` | 分期数 | 信用卡常见，1~N 期 |
| `payment_value` | 这笔支付金额 | 分期场景下单笔金额 |

**关键理解**：支付表和明细表是多对多偏多，一个订单多笔支付时 `payment_sequential` 递增，所以"订单实付总额"要 `GROUP BY order_id` 求和。

---

## 4. order_reviews（评价表）

一条记录 = 一条评价。**7 字段，99,224 行**。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `review_id` | 评价唯一 ID | 主键 |
| `order_id` | 关联订单 | 外键 → orders |
| `review_score` | 评分 | 1~5 分，**5 分最多**，用于满意度分析 |
| `review_comment_title` | 评价标题 | **大量缺失（8.7 万+）**，允许为空 |
| `review_comment_message` | 评价正文 | **大量缺失（5.8 万+）**，AI 文本分析只处理有文本的 |
| `review_creation_date` | 评价创建时间 | 评价时间分析 |
| `review_answer_timestamp` | 商家回复时间 | 可用于"响应速度"分析 |

**关键理解**：文本字段缺失严重是正常现象，别强行填。评分是定量分析主力，文本只做定性/AI 补充。

---

## 5. customers（客户表）

**5 字段，99,441 行**。无缺失。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `customer_id` | 客户记录 ID | 主键，**一个真实客户可能有多个**（换设备/重复下单） |
| `customer_unique_id` | 真实客户唯一 ID | **客户分析必须用它归并**，99,441 条里只有 96,096 个真实客户 |
| `customer_zip_code_prefix` | 客户邮编前缀（5 位） | 关联 geolocation 做地域分析 |
| `customer_city` | 城市 | 巴西城市，如 `sao paulo` |
| `customer_state` | 州 | 如 `SP`（圣保罗州） |

**关键理解**：`customer_id` vs `customer_unique_id` 是本项目最重要的业务区别之一。算"客户数/复购"要用 `customer_unique_id`，算"下单记录"用 `customer_id`。

---

## 6. products（产品表）

**9 字段，32,951 行**。注意：**没有真实商品名称**。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `product_id` | 商品 ID | 主键 |
| `product_category_name` | 商品类目（**葡语**） | 如 `perfumaria`，需翻译表转英文 |
| `product_name_lenght` | 商品名称长度 | ⚠️ 原字段名**拼写错误**（`lenght`），清洗时可改名或保持 |
| `product_description_lenght` | 描述长度 | ⚠️ 同样拼错 `lenght` |
| `product_photos_qty` | 照片数量 | 商品内容丰富度指标 |
| `product_weight_g` | 重量（克） | 物流分析可用 |
| `product_length_cm` | 长（厘米） | 体积尺寸 |
| `product_height_cm` | 高（厘米） | 体积尺寸 |
| `product_width_cm` | 宽（厘米） | 体积尺寸 |

**关键理解**：正因为没有商品名，所以产品模块要做成**"产品/类目运营分析"**（ID + 类目 + 属性 + 销售指标），而不是商品详情页。

---

## 7. sellers（卖家表）

**4 字段，3,095 行**。无缺失。

| 字段 | 含义 | 用途 |
|------|------|------|
| `seller_id` | 卖家 ID | 主键，关联 order_items |
| `seller_zip_code_prefix` | 卖家邮编前缀 | 关联地理表 |
| `seller_city` | 卖家城市 | 地域分析 |
| `seller_state` | 卖家州 | 地域分析 |

**关键理解**：卖家维度的所有"销售额、订单量、评分、履约"都是通过 `order_items.seller_id` 关联明细表算出来的，卖家表本身只是主体信息。

---

## 8. geolocation（地理表）

**5 字段，约 100 万行**。⚠️ **有约 26 万完全重复行，不能直接当"一行一邮编"的维度表用**。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `geolocation_zip_code_prefix` | 邮编前缀 | 关联 customers/sellers 的邮编 |
| `geolocation_lat` | 纬度 | 地图可视化 |
| `geolocation_lng` | 经度 | 地图可视化 |
| `geolocation_city` | 城市 | 地域 |
| `geolocation_state` | 州 | 地域 |

**关键理解**：同一邮编前缀会出现**多行**（经纬度略有差异）。进业务库前要先**去重 + 按 zip 前缀聚合经纬度**，否则地域分析会重复计数。

---

## 9. product_category_name_translation（类目翻译表）

**2 字段，71 行**。作用最单纯：把葡语类目名翻译成英文。

| 字段 | 含义 | 用途 / 注意点 |
|------|------|--------------|
| `product_category_name` | 类目名（葡语） | 关联 products |
| `product_category_name_english` | 类目名（英语） | 前端展示、报表用英文 |

**关键理解**：
- 这个表**有 BOM 头**（首列字段名前面有个不可见的 `\ufeff`），清洗时要 `encoding='utf-8-sig'` 读，否则字段名会带脏字符。
- 你 data 目录里实际只有一个翻译文件（文档提到有两个重复的，这里已是一个），用这一个即可。

---

## 三张表之间的"骨架关系"（记这张图就够）

```
customers.customer_id ──1:N──> orders.customer_id
orders.order_id ──1:N──> order_items.order_id  (且 order_items 同时连 products、sellers)
orders.order_id ──1:N──> order_payments.order_id
orders.order_id ──1:N──> order_reviews.order_id
products.product_category_name ──> category_translation.product_category_name
customers / sellers 的 zip_prefix ──> geolocation.zip_prefix
```

一句话总结：**orders 是枢纽**，向左连 customers，向右展开成 items/payments/reviews，items 再连 products 和 sellers，geolocation 和 translation 是辅助维度表。

---
