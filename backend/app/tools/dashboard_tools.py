from app.services.dashboard import get_sales_trend, get_category_ranking_info, get_products_ranking_info


def query_sales(db):
    return get_sales_trend(db)


def query_category(db, top):
    return get_category_ranking_info(db, top)


def query_product(db, top):
    return get_products_ranking_info(db, top)
