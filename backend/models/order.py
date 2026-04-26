from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str

class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

class OrderResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    total_amount: float
    status: str
    payment_method: Optional[str]
    shipping_address: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime
    paid_at: Optional[datetime]