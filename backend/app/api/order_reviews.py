from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.order_reviews import get_order_reviews

router = APIRouter()


@router.get("/reviews")
def list_order_reviews(db: Session = Depends(get_db), page: int = 1, page_size: int = 20):
    reviews = get_order_reviews(db, page, page_size)
    return {
        "items": [
            {
                "review_id": r.review_id,
                "order_id": r.order_id,
                "review_score": r.review_score,
                "review_comment_title": r.review_comment_title,
                "review_comment_message": r.review_comment_message,
                "review_creation_date": r.review_creation_date,
                "review_answer_timestamp": r.review_answer_timestamp,
            }
            for r in reviews
        ]
    }
