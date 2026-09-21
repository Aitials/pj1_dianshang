from sqlalchemy.orm import Session

from app.repositories.dashboard import avg_reviews


def get_avg_reviews(db: Session):
    return avg_reviews(db)
