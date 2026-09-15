from sqlalchemy import Column, DateTime, Integer, String

from app.db.session import Base


class OrderReview(Base):
    __tablename__ = "olist_order_reviews_dataset_clean"

    review_id = Column(String(35), primary_key=True)
    order_id = Column(String(35), nullable=False)
    review_score = Column(Integer, nullable=False)
    review_comment_title = Column(String(50))
    review_comment_message = Column(String(500))
    review_creation_date = Column(DateTime)
    review_answer_timestamp = Column(DateTime)
