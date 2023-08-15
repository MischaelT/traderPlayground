from exchange_imitator.models.orders.base_order import BaseOrder


class StopLimitOrder(BaseOrder):

    def __init__(self, order_type, quantity,
                 ticker, direction, execution_price, stop_price, timeframe) -> None:

        self.execution_price = execution_price
        self.stop_price = stop_price

        self.blocked_balance = 0

        super().__init__(order_type, quantity, ticker, direction, timeframe)

    def cancel_order(self):
        return self.order_id
