from fastapi import APIRouter, Depends ,Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.repositories.order_reviews import get_order_reviews

router = APIRouter()


@router.get("/reviews" ,dependencies=[Depends(require_permission("order:read"))])
def list_order_reviews(db: Session = Depends(get_db),page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100)):
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
