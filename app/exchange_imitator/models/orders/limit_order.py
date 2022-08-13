from exchange_imitator.models.orders.base_order import BaseOrder


class LimitOrder(BaseOrder):

    def __init__(self, order_type, quantity,
                 asset_name, direction, execution_price, timeframe) -> None:

        self.execution_price = execution_price

        self.blocked_balance = 0

        super().__init__(order_type, quantity, asset_name, direction, timeframe)

    def cancel_order(self):
        return self.order_id
