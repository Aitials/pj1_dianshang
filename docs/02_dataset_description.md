# 数据集描述（Dataset Description）

> 项目：电商运营管理与智能分析平台
> 对应论文章节：相关数据与需求分析

## 1. 数据来源

| 项目 | 说明 |
|------|------|
| 数据集名称 | Olist Brazilian E-Commerce Public Dataset |
| 数据性质 | 巴西电商平台 Olist 的**匿名化历史交易数据** |
| 订单时间范围 | 2016-09-04 ~ 2018-10-17 |
| 数据体量 | 订单 99,441 笔、订单明细 112,650 条、产品 32,951 个、卖家 3,095 个 |
| 原始语言 | 葡萄牙语（类目名、城市名、州名） |

## 2. 数据文件清单

| 文件 | 行数 | 字段数 | 核心职责 |
|------|------|--------|----------|
| olist_customers_dataset.csv | 99,441 | 5 | 客户与地区主体 |
| olist_geolocation_dataset.csv | 1,000,163 | 5 | 邮编前缀与经纬度 |
| olist_order_items_dataset.csv | 112,650 | 7 | 订单商品明细、卖家、价格、运费 |
| olist_order_payments_dataset.csv | 103,886 | 5 | 支付方式、分期、金额 |
| olist_order_reviews_dataset.csv | 99,224 | 7 | 评分、评价文本、评价时间 |
| olist_orders_dataset.csv | 99,441 | 8 | 订单生命周期与时间线 |
| olist_products_dataset.csv | 32,951 | 9 | 产品 ID、类目、尺寸重量、内容质量字段 |
| olist_sellers_dataset.csv | 3,095 | 4 | 卖家及地区 |
| product_category_name_translation.csv | 71 | 2 | 葡语类目到英语类目映射 |

## 3. 业务结构：事实表 vs 维度表

### 事实表（记录"发生了什么"，数据量大）
- **orders**：订单生命周期与时间线
- **order_items**：订单商品明细（销售金额的真正来源）
- **order_payments**：支付记录
- **order_reviews**：评价记录

### 维度表（描述"谁/什么"，用于关联与分组）
- **customers**：客户主体
- **products**：产品属性
- **sellers**：卖家主体
- **geolocation**：地理位置
- **category_translation**：类目翻译

## 4. 表间关系（ER 骨架）

```
customers.customer_id       1 ── N  orders.customer_id
orders.order_id             1 ── N  order_items.order_id
products.product_id         1 ── N  order_items.product_id
sellers.seller_id           1 ── N  order_items.seller_id
orders.order_id             1 ── N  order_payments.order_id
orders.order_id             1 ── N  order_reviews.order_id
products.product_category_name ── category_translation.product_category_name
customers.customer_zip_code_prefix ── geolocation.geolocation_zip_code_prefix
sellers.seller_zip_code_prefix    ── geolocation.geolocation_zip_code_prefix
```

## 5. 数据的关键事实（必须记住）

1. **products 没有真实商品名称**，只有 product_id、类目、尺寸重量、照片数量等属性。因此产品模块做"产品/类目运营分析"，而非商城商品详情页。
2. **customer_id 不等于真实客户**。同一真实客户（customer_unique_id）可能对应多个 customer_id（换设备/重复下单）。客户分析必须用 customer_unique_id 归并。
3. **订单时间字段存在缺失**：approved 缺 160、carrier 缺 1,783、customer delivered 缺 2,965，按业务语义保留 NULL。
4. **评价文本大量缺失**：title 缺 87,656、message 缺 58,247，AI 文本分析只处理有文本的记录。
5. **geolocation 有约 26 万完全重复行**，且同一邮编前缀有多行，需先去重再聚合。
6. **数据是历史样本（2016–2018）**，不是实时数据；当前外部信息（政策、新闻）需由联网搜索补充。
