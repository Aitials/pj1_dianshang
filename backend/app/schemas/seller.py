from pydantic import BaseModel

class SellerResponse(BaseModel):
    seller_id : str
    seller_zip_code_prefix : str
    seller_city : str
    seller_state : str
    class Config:
        from_attributes = True

class Seller_rankitem_Response(BaseModel):
    seller_id : str
    sales : float
    order_count : int

class SellerRankResponse(BaseModel):
    rank : list[Seller_rankitem_Response]

class Seller_reviewit_Response(BaseModel):
    seller_id : str
    avg_score : float
    review_count : int

class Seller_reviewResoinse(BaseModel):
    top : int
    review_rank : list[Seller_reviewit_Response]