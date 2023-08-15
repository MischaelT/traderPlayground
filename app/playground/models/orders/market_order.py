from exchange_imitator.models.orders.base_order import BaseOrder


class MarketOrder(BaseOrder):

    def __init__(self, direction, order_type, quantity,
                 asset_name, execution_price, timeframe) -> None:

        self.execution_price = execution_price

        super().__init__(order_type, quantity, asset_name, direction, timeframe)

    def cancel_order(self):
        return self.order_id
