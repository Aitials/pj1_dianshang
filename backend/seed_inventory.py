"""
库存全量初始化脚本
================
功能: 让 olist_products_dataset_clean 中"每一个商品"都在 inventory 有库存信息,
      且每个商品在 inventory_log 至少有 1~2 条库存日志。

约定(与已有项目一致):
  - inventory      : product_id(PK) / quantity / safety_stock
  - inventory_log  : id(自增) / product_id / change / before / after / reason / operator / created_at
  - 每条 log 满足 before + change = after, 且该商品"最新一条"log 的 after == 当前库存 quantity
  - product_id 全部取自 olist_products_dataset_clean, 外键可对上

说明:
  - 保留已存在的 inventory 记录(仅补缺), 不删除商品库存。
  - inventory_log 会重建为"每个商品 2 条自洽日志", 保证整体一致性。
使用方法:
  cd backend && python seed_inventory.py
"""
import os
import random
import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

SEED = 7

# 连接信息不再硬编码：本地跑读 backend/.env，容器里跑读 compose 注入的 DATABASE_URL，
# 否则容器内 localhost 会指向自身而不是 mysql 服务。
load_dotenv(Path(__file__).resolve().parent / ".env")
_db_url = make_url(os.getenv("DATABASE_URL"))
CONN = dict(host=_db_url.host, port=_db_url.port or 3306, user=_db_url.username,
            password=_db_url.password, database=_db_url.database, charset="utf8mb4")

REASONS = ['期初库存初始化', '采购入库', '出库发货', '盘点调整', '退货入库']
OPERATORS = ['admin', 'warehouse_01', 'warehouse_02', 'operator_zhang', 'operator_li']
BASE_TIME = datetime.datetime(2026, 9, 12, 9, 0, 0)


def main():
    rnd = random.Random(SEED)
    conn = pymysql.connect(**CONN)
    cur = conn.cursor()

    # 1. 取全部商品
    cur.execute("SELECT product_id FROM olist_products_dataset_clean")
    products = [r[0] for r in cur.fetchall()]
    total = len(products)
    print("商品总数:", total)

    # 2. 已有库存的商品(巩固成果, 不删除), 保留其实际库存量以保证 log 一致
    cur.execute("SELECT product_id, quantity, safety_stock FROM inventory")
    existing = {}
    for pid, q, s in cur.fetchall():
        existing[pid] = (q, s)
    print("已有库存商品数:", len(existing))

    # 3. 为缺库存的商品生成 inventory 记录(唯一索引防重)
    inv_rows = []
    inv_records = {}  # product_id -> (quantity, safety_stock)
    for pid in products:
        if pid in existing:
            inv_records[pid] = existing[pid]          # 复用已有库存
        else:
            quantity = rnd.randint(100, 2000)
            safety = rnd.randint(20, 150)
            inv_records[pid] = (quantity, safety)
            inv_rows.append((pid, quantity, safety))
    cur.executemany(
        "INSERT INTO inventory (product_id, quantity, safety_stock) "
        "VALUES (%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE quantity=VALUES(quantity), safety_stock=VALUES(safety_stock)",
        inv_rows,
    )
    conn.commit()
    print("本次补插 inventory 行数:", len(inv_rows))

    # 4. 重建 inventory_log: 每个商品 2 条自洽日志, 最新一条 after == 当前库存
    cur.execute("DELETE FROM inventory_log")
    log_rows = []
    for i, pid in enumerate(products, 1):
        quantity, safety = inv_records[pid]
        q = max(quantity, 5)
        x = rnd.randint(10, max(10, q // 2))  # 第二次变动量
        after1 = q - x
        # log1 期初: before=0 -> after1
        t1 = BASE_TIME + datetime.timedelta(hours=i)
        log_rows.append((pid, after1, 0, after1, '期初库存初始化', OPERATORS[0], t1))
        # log2 入库: before=after1 -> after=q(当前库存)
        t2 = t1 + datetime.timedelta(hours=6)
        log_rows.append((pid, x, after1, q, '采购入库', OPERATORS[1], t2))

    cur.executemany(
        "INSERT INTO inventory_log (product_id, `change`, `before`, `after`, reason, operator, created_at) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        log_rows,
    )
    conn.commit()
    print("本次插入 inventory_log 行数:", len(log_rows))

    # 5. 校验
    cur.execute("SELECT COUNT(*) FROM inventory")
    print("inventory 最终:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM inventory_log")
    print("inventory_log 最终:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM olist_products_dataset_clean p LEFT JOIN inventory i ON p.product_id=i.product_id WHERE i.product_id IS NULL")
    print("缺库存的商品数:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM olist_products_dataset_clean p LEFT JOIN inventory_log l ON p.product_id=l.product_id WHERE l.product_id IS NULL")
    print("无日志的商品数:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM inventory_log WHERE `before`+`change` <> `after`")
    print("before+change!=after 行数:", cur.fetchone()[0])
    # 每个商品"最新一条"log 的 after 必须 == 当前库存
    cur.execute(
        "SELECT COUNT(*) FROM (SELECT l.product_id, l.`after`, l.created_at, "
        "ROW_NUMBER() OVER (PARTITION BY l.product_id ORDER BY l.created_at DESC, l.id DESC) rn "
        "FROM inventory_log l) t "
        "JOIN inventory i ON i.product_id=t.product_id "
        "WHERE t.rn=1 AND t.`after` != i.quantity")
    print("最新log.after!=当前库存 行数:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM inventory_log l LEFT JOIN olist_products_dataset_clean p ON l.product_id=p.product_id WHERE p.product_id IS NULL")
    print("log 外键悬空数:", cur.fetchone()[0])

    conn.close()


if __name__ == '__main__':
    main()