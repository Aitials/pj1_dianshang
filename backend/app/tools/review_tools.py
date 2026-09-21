from sqlalchemy.orm import Session

from app.services.reviews import get_avg_reviews


def query_review(db: Session):
    return {
        "avg_review_score": get_avg_reviews(db)
    }
