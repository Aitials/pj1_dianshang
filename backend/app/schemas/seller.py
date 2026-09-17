from pydantic import BaseModel

class SellerResponse(BaseModel):
    seller_id : str
    seller_zip_code_prefix : str
    seller_city : str
    seller_state : str
    class Config:
        from_attributes = True