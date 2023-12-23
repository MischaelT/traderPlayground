from pydantic import BaseModel
from typing import Optional

class Order(BaseModel):
    order_type: str
    quantity: int
    base_asset: str
    target_asset: str
    direction: str
    execution_price: float
    stop_price: Optional[float] = None
    signal_price: Optional[float] = None
    blocked_amount: Optional[float] = None



