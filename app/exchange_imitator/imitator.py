from data.choices import D1

from utils.logging import logger

from exchange_imitator.exchange import DemoExchange


class Imitator():

    """
        Class DemoManager is exchange manager for testing and provides methods for interaction with DemoExchange
    """

    def __init__(self, user_balance: int, trading_list: list, ticks_for_test: int,
                 comission: float, multi_timeframes: bool = False, timeframe=D1) -> None:

        self.__exchange = DemoExchange(user_balance, trading_list, ticks_for_test, multi_timeframes, timeframe, comission=comission)

        self.__klines_generator = self.__exchange.tick_generator()

        self.current_klines = {}

        super().__init__()

    def get_kline(self, ticker):

        return self.current_klines.get(ticker)

    def check_connection(self):
        try:

            self.current_klines = next(self.__klines_generator)
        except StopIteration:
            logger.info('PROCESS_FINISHED')

        return True

    def place_market_order(self, order_direction, ticker, quantity, timeframe):

        order_id = self.__exchange.place_market_order(direction=order_direction,
                                                      ticker=ticker, quantity=quantity, timeframe=timeframe)

        return order_id

    def place_limit_order(self, order_direction, ticker, quantity, price, timeframe):

        order_id = self.__exchange.place_limit_order(direction=order_direction, ticker=ticker,
                                                     quantity=quantity, price=price, timeframe=timeframe)

        return order_id

    def place_stopLimit_order(self, order_direction, ticker, limit_price, stop_price, quantity, timeframe):

        order_id = self.__exchange.place_stopLimit_order(direction=order_direction, ticker=ticker,
                                                         quantity=quantity, stop_price=stop_price,
                                                         limit_price=limit_price, timeframe=timeframe)

        return order_id

    def place_OCO_order(self):
        pass

    def cancel_order(self, order_id):
        self.__exchange.cancel_order(order_id)

    def get_open_orders(self):
        return self.__exchange.orders_list

    def get_asset_balance(self):
        pass

    def get_statistics(self):

        return self.__exchange.get_statistics()
