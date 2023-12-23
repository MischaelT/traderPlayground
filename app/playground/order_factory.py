import inspect
from datetime import datetime
from typing import Tuple, Union
from app.data.choices import order_classes
from app.data.models import BaseOrder
from app.utils.logger import logger


class OrderFactory:
    @staticmethod
    def create_order(order_data) -> Tuple[Union[BaseOrder, None], dict]:
        order_type = order_data.__dict__.get('order_type', None)

        if not order_type:
            return None, {'message': 'order_type must be provided'}
        
        order_class = order_classes.get(order_type, None)

        if not order_class:
            return None, {'message': f"Invalid order type: {order_type}"}

        constructor_args = inspect.getfullargspec(order_class.__init__).args[1:]

        if not all(arg in order_data for arg in constructor_args):
            logger.error()
            return None, {'message': 'Not all of the arguments were provided'}

        order_data = {key: value for key, value in order_data.__dict__.items() if key in constructor_args}

        order = order_class(
            creation_date=datetime.now(),
            **order_data
        )

        return order, {}
