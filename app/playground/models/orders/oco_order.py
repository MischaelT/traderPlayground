from exchange_imitator.models.orders.base_order import BaseOrder


class OcoOrder(BaseOrder):

    def __init__(self, order_type, quantity,
                 asset_name, direction, execution_price,
                 signal_price, blocked_amount, bounded_order_id, timeframe) -> None:

        self.execution_price = execution_price
        self.signal_price = signal_price

        self.blocked_balance = blocked_amount

        self.bounded_order_id = bounded_order_id

        super().__init__(order_type, quantity, asset_name, direction, timeframe)

    def cancel_order(self):
        return (self.order_id, self.bounded_order_id)
