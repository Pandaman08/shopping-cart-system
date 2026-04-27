from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int

class CartItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    product_price: float
    quantity: int
    unit_price: float
    subtotal: float

class CartResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItemResponse]
    total: float
    item_count: int
    created_at: datetime
    updated_at: datetime