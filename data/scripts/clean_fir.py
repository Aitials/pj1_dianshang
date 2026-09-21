import os
from pathlib import Path

import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine

# data/scripts/clean_fir.py -> parents[2] 即项目根目录，原始 CSV 固定放在 data/raw/ 下
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"

# 连接串从 backend/.env 读取，不再把账号密码写在脚本里
load_dotenv(BASE_DIR / "backend" / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("未找到 DATABASE_URL，请先在 backend/.env 中配置（可参考 backend/.env.example）")

customers = pd.read_csv(RAW_DIR / 'olist_customers_dataset.csv', dtype={"customer_zip_code_prefix": str})
customers['customer_zip_code_prefix'] =  customers['customer_zip_code_prefix'].astype(str)
customers['customer_city'] = customers['customer_city'].str.strip()

engine = create_engine(DATABASE_URL)

customers.to_sql('olist_customers_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_customers_dataset_clean写入成功！')

geo = pd.read_csv(RAW_DIR / 'olist_geolocation_dataset.csv',dtype={"geolocation_zip_code_prefix": str} )
geo = geo.drop_duplicates()
def get_mode(ser):
    m = ser.mode()
    if m.empty:
        return None
    return m.iloc[0]
geo = geo.groupby('geolocation_zip_code_prefix').agg({'geolocation_lat':'mean','geolocation_lng':'mean','geolocation_city':get_mode,'geolocation_state':get_mode}).reset_index()
geo.to_sql('olist_geolocation_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_geolocation_dataset_clean写入成功！')

ord_i = pd.read_csv(RAW_DIR / 'olist_order_items_dataset.csv')
ord_i.to_sql('olist_order_items_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_order_items_dataset_clean写入成功！')

ord_p = pd.read_csv(RAW_DIR / 'olist_order_payments_dataset.csv')
ord_p = ord_p.drop(ord_p.query('payment_type not in ["credit_card","boleto","voucher","debit_card","not_defined"]').index)
ord_p.to_sql('olist_order_payments_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_order_payments_dataset_clean写入成功！')

ord_r = pd.read_csv(RAW_DIR / 'olist_order_reviews_dataset.csv')
ord_r = ord_r.drop_duplicates('review_id')
ord_r = ord_r.drop(ord_r.query('review_score not in [1,2,3,4,5]').index)
ord_r.to_sql('olist_order_reviews_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_order_reviews_dataset_clean写入成功！')

ord_rs = pd.read_csv(RAW_DIR / 'olist_orders_dataset.csv')
ord_rs = ord_rs.drop(ord_rs.query('order_status not in ["delivered","invoiced","shipped","processing","unavailable","canceled","created","approved"]').index)
ord_rs.to_sql('olist_orders_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_order_orders_dataset_clean写入成功！')

products  = pd.read_csv(RAW_DIR / 'olist_products_dataset.csv')
products['product_category_name'] = products['product_category_name'].fillna('unknown')
products = products.drop(products.query('product_photos_qty < 0').index)
products['product_name_length'] = products['product_name_lenght']
products['product_description_length'] = products['product_description_lenght']
products = products.drop(['product_description_lenght', 'product_name_lenght'], axis='columns')
products.to_sql('olist_products_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_products_dataset_clean写入成功！')

sellers = pd.read_csv(RAW_DIR / 'olist_sellers_dataset.csv', dtype={"seller_zip_code_prefix": str})
sellers['seller_city'] = sellers['seller_city'].str.strip()
sellers.to_sql('olist_sellers_dataset_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('olist_sellers_dataset_clean写入成功！')

trans = pd.read_csv(RAW_DIR / 'product_category_name_translation.csv', encoding='utf-8-sig')
trans.to_sql('product_category_name_translation_clean', con=engine, index=False, if_exists='append', chunksize=1000)
print('product_category_name_translation_clean写入成功！')






