from pydantic import BaseModel


class ProductResponse(BaseModel):
    product_id: str
    product_category_name: str
    product_name_length: int | None = None
    product_description_length: int | None = None
    product_photos_qty: int | None = None
    product_weight_g: int | None = None
    product_length_cm: int | None = None
    product_height_cm: int | None = None
    product_width_cm: int | None = None

    class Config:
        from_attributes = True