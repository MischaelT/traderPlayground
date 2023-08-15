import uuid
from abc import ABC, abstractmethod


class BaseOrder(ABC):

    def __init__(self, order_type, quantity,
                 asset_name, direction, timeframe) -> None:

        self.order_id = uuid.uuid4()
        self.order_type = order_type
        self.quantity = quantity
        self.asset_name = asset_name
        self.direction = direction
        self.timeframe = timeframe

    @abstractmethod
    def cancel_order():
        pass
