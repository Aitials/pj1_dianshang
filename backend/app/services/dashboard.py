from sqlalchemy.orm import Session

from app.repositories.dashboard import sales_trend, get_category_ranking, get_productsranking


def get_sales_trend(db: Session):
    return sales_trend(db)


def get_category_ranking_info(db: Session, top):
    return get_category_ranking(db, top)


def get_products_ranking_info(db: Session, top):
    return get_productsranking(db, top)
