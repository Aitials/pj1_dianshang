# -*- coding: utf-8 -*-
"""
validate_raw.py
数据质量检查脚本：对 data/raw/ 下的 9 张原始 CSV 做统计，
输出到 data/quality/data_quality_stats.md

不依赖第三方库，使用标准库 csv，保证任何环境可复现。
"""
import csv
import os
import sys
from collections import Counter

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quality')
os.makedirs(OUT_DIR, exist_ok=True)

FILES = [
    'olist_customers_dataset.csv',
    'olist_geolocation_dataset.csv',
    'olist_order_items_dataset.csv',
    'olist_order_payments_dataset.csv',
    'olist_order_reviews_dataset.csv',
    'olist_orders_dataset.csv',
    'olist_products_dataset.csv',
    'olist_sellers_dataset.csv',
    'product_category_name_translation.csv',
]

# 需要做枚举值检查的字段
ENUM_FIELDS = {
    'olist_orders_dataset.csv': ['order_status'],
    'olist_order_payments_dataset.csv': ['payment_type'],
    'olist_order_reviews_dataset.csv': ['review_score'],
}

# 需要做时间范围检查的字段
TIME_FIELDS = {
    'olist_orders_dataset.csv': [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
    ],
}

# 需要做主键唯一性检查的字段
PK_FIELDS = {
    'olist_customers_dataset.csv': ['customer_id'],
    'olist_geolocation_dataset.csv': ['geolocation_zip_code_prefix'],
    'olist_order_items_dataset.csv': ['order_id', 'order_item_id'],
    'olist_order_payments_dataset.csv': ['order_id', 'payment_sequential'],
    'olist_order_reviews_dataset.csv': ['review_id'],
    'olist_orders_dataset.csv': ['order_id'],
    'olist_products_dataset.csv': ['product_id'],
    'olist_sellers_dataset.csv': ['seller_id'],
    'product_category_name_translation.csv': ['product_category_name'],
}


def read_rows(path):
    encodings = ['utf-8-sig', 'utf-8']
    for enc in encodings:
        try:
            with open(path, encoding=enc, newline='') as f:
                r = csv.DictReader(f)
                return list(r)
        except UnicodeDecodeError:
            continue
    raise RuntimeError('cannot read ' + path)


def main():
    out_lines = []
    out_lines.append('# 原始数据质量统计报告')
    out_lines.append('')
    out_lines.append('> 由 validate_raw.py 自动生成')
    out_lines.append('')
    out_lines.append('| 文件 | 行数 | 字段数 | 缺失单元格 | 完全重复行 |')
    out_lines.append('|------|------|--------|------------|------------|')

    stats = {}
    for fn in FILES:
        path = os.path.join(BASE, fn)
        rows = read_rows(path)
        fieldnames = list(rows[0].keys()) if rows else []
        n_rows = len(rows)
        n_cols = len(fieldnames)
        n_missing = 0
        for row in rows:
            for k in fieldnames:
                v = row.get(k)
                if v is None or v == '':
                    n_missing += 1
        # 完全重复行
        seen = set()
        dup = 0
        for row in rows:
            key = tuple(row.get(k) for k in fieldnames)
            if key in seen:
                dup += 1
            else:
                seen.add(key)
        stats[fn] = {
            'rows': rows, 'n_rows': n_rows, 'n_cols': n_cols,
            'n_missing': n_missing, 'dup': dup, 'fieldnames': fieldnames,
        }
        out_lines.append(f'| {fn} | {n_rows} | {n_cols} | {n_missing} | {dup} |')

    out_lines.append('')

    # 枚举值分布
    out_lines.append('## 枚举值分布')
    for fn, fields in ENUM_FIELDS.items():
        rows = stats[fn]['rows']
        for field in fields:
            c = Counter(row.get(field) for row in rows)
            out_lines.append(f'')
            out_lines.append(f'### {fn} :: {field}')
            for val, cnt in sorted(c.items(), key=lambda x: -x[1]):
                out_lines.append(f'- {val}: {cnt}')

    out_lines.append('')

    # 主键唯一性
    out_lines.append('## 主键唯一性检查')
    for fn, fields in PK_FIELDS.items():
        rows = stats[fn]['rows']
        seen = set()
        dup = 0
        for row in rows:
            key = tuple(row.get(k) for k in fields)
            if key in seen:
                dup += 1
            else:
                seen.add(key)
        n_uniq = len(seen)
        out_lines.append(f'- {fn} 主键 {fields}: 总行 {len(rows)}，唯一 {n_uniq}，重复 {dup}')

    out_lines.append('')

    # 时间范围
    out_lines.append('## 时间字段范围')
    for fn, fields in TIME_FIELDS.items():
        rows = stats[fn]['rows']
        for field in fields:
            vals = [row.get(field) for row in rows if row.get(field)]
            if vals:
                out_lines.append(f'- {fn} :: {field}: min={min(vals)} max={max(vals)} 缺失={len(rows)-len(vals)}')
            else:
                out_lines.append(f'- {fn} :: {field}: 全空')

    out_lines.append('')

    # 每字段缺失数明细
    out_lines.append('## 各字段缺失数明细')
    for fn in FILES:
        rows = stats[fn]['rows']
        fieldnames = stats[fn]['fieldnames']
        out_lines.append(f'')
        out_lines.append(f'### {fn}')
        for k in fieldnames:
            miss = sum(1 for row in rows if row.get(k) in (None, ''))
            if miss > 0:
                out_lines.append(f'- {k}: 缺失 {miss}')

    out_path = os.path.join(OUT_DIR, 'data_quality_stats.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
    print('written:', out_path)
    print('\n'.join(out_lines))


if __name__ == '__main__':
    main()
