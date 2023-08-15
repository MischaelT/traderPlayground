from typing import Dict, List, Union

from data.choices import BUY, D1, H1, H4, LIMIT, MARKET, OCO, SELL, STOP_LIMIT
from data.consts import SUPPORTED_LIST
from data.postgres import PostgresDB

from utils.logging import logger

from exchange_imitator.models.kline import Kline
from exchange_imitator.models.orders.limit_order import LimitOrder
from exchange_imitator.models.orders.market_order import MarketOrder
from exchange_imitator.models.orders.oco_order import OcoOrder
from exchange_imitator.models.orders.stopLimit_order import StopLimitOrder
from exchange_imitator.models.user import User


class DemoExchange():

    """
        Class that imitates flow of exchange on historical data from database

    """

    # TODO Implement OCO orders
    # TODO Implement exchange comission

    def __init__(self, user_balance, trading_list, ticks_for_test, multi_timeframes, timeframe, comission) -> None:

        self.db: PostgresDB = PostgresDB()

        self.orders_list: List[Union[StopLimitOrder, MarketOrder, OcoOrder, LimitOrder]] = []
        self.assets_list = SUPPORTED_LIST
        self.ticks_for_test = ticks_for_test

        self.multi_timeframes = multi_timeframes
        self.timeframe = timeframe

        self.user = User(user_balance, trading_list)

        self.one_tick = 0
        self.current_klines: Dict[Dict[Kline]] = None
        self.tick_number = 1
        self.current_time = 0

        self.comission = comission

        self.__initialize_timeframe()

    def tick_generator(self):

        tick_number = 0

        while (tick_number < self.ticks_for_test):

            logger.info('Day Begins')
            logger.info(f'User balance: {self.user.account_balance}')
            logger.info(f'Asset balance: {self.user.asset_balance}')

            if self.multi_timeframes:
                klines_data = self.__get_multitimeframes_result(tick_number=tick_number)
            else:
                klines_data = self.__get_oneTimeframe_result()

            result = self.__create_klines(klines_data)

            yield result

            self.__manage_orders()
            tick_number += 1

            self.current_time += self.one_tick

            logger.info('Day ends')
            logger.info('________________________________________')

    def place_market_order(self, direction, ticker, quantity, timeframe):

        logger.info('Market order has been placed')

        order_type = MARKET

        price = self.current_klines[ticker][timeframe].get_average_price()

        not_null_balance = self.__is_not_null_balance(ticker, direction=direction, quantity=quantity, price=price)

        if not_null_balance:

            order = MarketOrder(order_type=order_type,
                                quantity=quantity, asset_name=ticker,
                                execution_price=price, direction=direction, timeframe=timeframe)

            self.orders_list.append(order)

            return order.order_id

        else:
            logger.info('Not enought money')

    def place_limit_order(self, direction, ticker, quantity, price, timeframe):

        logger.info(f'Limit order has been placed on price {price}')

        order_type = LIMIT

        not_null_balance = self.__is_not_null_balance(ticker, direction=direction, quantity=quantity, price=price)  # noqa

        if not_null_balance:

            order = LimitOrder(order_type=order_type, quantity=quantity,
                               execution_price=price, direction=direction, asset_name=ticker, timeframe=timeframe)

            self.__block_balance(order)
            self.orders_list.append(order)

            return order.order_id

        else:
            logger.info('Not enought money')

    def place_stopLimit_order(self, direction, ticker, quantity, limit_price, stop_price, timeframe):

        order_type = STOP_LIMIT

        not_null_balance = self.__is_not_null_balance(ticker, direction=direction, quantity=quantity, price=limit_price)  # noqa

        if not_null_balance:

            logger.debug(order_type)

            order = StopLimitOrder(quantity=quantity, ticker=ticker,
                                   execution_price=limit_price, stop_price=stop_price,
                                   direction=direction, order_type=order_type, timeframe=timeframe)

            logger.info('StopLimit order has been placed')

            self.__block_balance(order)
            self.orders_list.append(order)

            return order.order_id

        else:

            logger.info('Not enought money')

    def place_OCO_order(self, order_type, quantity, ticker, direction, execution_price,
                        signal_price, blocked_amount, bounded_order_id, timeframe):
        pass

    def cancel_order(self, order_id):

        for order in self.orders_list:

            if order.order_id == order_id:
                self.__unblock_balance(order)
                self.orders_list.remove(order)
                cancelled_order_id = order.cancel_order()

                logger.info(cancelled_order_id)

    def get_statistics(self):
        pass

    def __get_multitimeframes_result(self, tick_number):

        result = {}

        for asset in self.assets_list:
            try:
                asset_dict = {}

                if tick_number % 4 == 0:
                    row = self.db.get_kline_by_time(time=self.current_time, table_name=asset, timeframe=H4)
                    asset_dict[H4] = row[0]

                if tick_number % 24 == 0:
                    row = self.db.get_kline_by_time(time=self.current_time, table_name=asset, timeframe=D1)
                    asset_dict[D1] = row[0]

                row = self.db.get_kline_by_time(time=self.current_time, table_name=asset, timeframe=H1)

                asset_dict[H1] = row[0]

                result[asset] = asset_dict

            except Exception as e:
                logger.debug(e)

        return result

    def __get_oneTimeframe_result(self):

        result = {}

        for asset in self.assets_list:
            row = self.db.get_kline_by_time(self.current_time, table_name=asset, timeframe=self.timeframe)
            result[asset] = row[0]

        return result

    def __create_klines(self, klines: dict):

        """
            Method that creates Klines objects from klines dict
        """

        result = {i: [] for i in self.user.trading_list}

        if self.multi_timeframes:

            for asset in result:

                asset_klines = klines[asset]

                for timeframe in asset_klines:

                    kline_data = asset_klines[timeframe]

                    kline = Kline(tick=self.tick_number,
                                  open_price=kline_data[1],
                                  high_price=kline_data[2],
                                  low_price=kline_data[3],
                                  close_price=kline_data[4],
                                  timeframe=timeframe)

                    result[asset].append(kline)
        else:
            for asset in result:

                kline_data = klines[asset]

                kline = Kline(tick=self.tick_number,
                              open_price=kline_data[1],
                              high_price=kline_data[2],
                              low_price=kline_data[3],
                              close_price=kline_data[4],
                              timeframe=self.timeframe)

                result[asset].append(kline)

        return result

    def __initialize_timeframe(self):

        """
            Method initialize timeframes based on config settings
        """

        if not self.multi_timeframes:

            if self.timeframe == H1:
                self.one_tick = 3600
                self.tick_number = self.ticks_for_test * 24
            elif self.timeframe == H4:
                self.one_tick = 3600 * 4
                self.tick_number = self.ticks_for_test * 4
            elif self.timeframe == D1:
                self.one_tick = 3600 * 24
                self.tick_number = self.ticks_for_test
        else:
            self.one_tick = 3600
            self.tick_number = self.ticks_for_test * 24

        self.current_time = self.db.get_latest_klines(timeframe=D1, number=1, table_name=self.assets_list[0])[0][0] - self.one_tick * self.tick_number  # noqa
        logger.debug(self.current_time)

    def __is_not_null_balance(self, ticker, direction, quantity, price) -> bool:

        """
            Method checks if it is possible to buy or sell asset.

        Returns:
            bool: True if balance after deal>0, False if balance<0
        """

        if direction == BUY:
            balance = self.user.account_balance - quantity * price * (1 + self.comission)
        elif direction == SELL:
            balance = self.user.asset_balance[ticker] - quantity

        if balance >= 0:
            return True

        return False

    def __manage_orders(self):

        logger.info('Managing orders...')

        for order in self.orders_list:

            if order.order_type == MARKET:
                self.__process_market_order(order)

            elif order.order_type == LIMIT:
                self.__process_limit_order(order)

            elif order.order_type == STOP_LIMIT:
                self.__process_stopLimit_order(order)

            elif order.order_type == OCO:
                self.__process_OCO_order(order)

    def __block_balance(self, order: Union[LimitOrder, StopLimitOrder, OcoOrder]):

        if order.direction == SELL:

            order.blocked_balance = order.quantity
            self.user.asset_balance[order.asset_name] -= order.blocked_balance
            logger.debug(order.blocked_balance)

        elif order.direction == BUY:

            order.blocked_balance = order.quantity * order.execution_price * (1 + self.comission)
            self.user.account_balance -= order.blocked_balance
            logger.debug(order.blocked_balance)

    def __unblock_balance(self, order: Union[LimitOrder, StopLimitOrder, OcoOrder]):

        if order.direction == SELL:

            self.user.asset_balance[order.asset_name] += order.blocked_balance

        elif order.direction == BUY:

            self.user.account_balance += order.blocked_balance

    def __process_market_order(self, order: MarketOrder):
        logger.info('Market order processed')
        self.__execute_order(order)

        self.orders_list.remove(order)

    def __process_limit_order(self, order: LimitOrder):

        is_executed = False
        logger.info('Limit order processed')

        if self.current_klines[order.asset_name][order.timeframe].get_average_price() <= order.execution_price and order.direction == BUY:  # noqa

            self.user.account_balance += order.blocked_balance

            market_order = MarketOrder(direction=order.direction, quantity=order.quantity,
                                       asset_name=order.asset_name, execution_price=order.execution_price,
                                       order_type=MARKET)

            self.__execute_order(market_order)

            is_executed = True

        elif self.current_klines[order.asset_name][order.timeframe].get_average_price() >= order.execution_price and order.direction == SELL:  # noqa

            self.user.asset_balance += order.blocked_balance

            market_order = MarketOrder(direction=order.direction, quantity=order.quantity,
                                       asset_name=order.asset_name, execution_price=order.execution_price,
                                       order_type=MARKET)

            self.__execute_order(market_order)

            is_executed = True

        if is_executed:
            self.orders_list.remove(order)

        return is_executed

    def __process_stopLimit_order(self, order: StopLimitOrder):
        logger.info('StopLimit order processed')
        is_executed = False

        if self.current_klines[order.asset_name][order.timeframe].get_average_price() <= order.stop_price and order.direction == BUY:  # noqa

            limit_order = LimitOrder(order_type=LIMIT, quantity=order.quantity, asset_name=order.asset_name,
                                     direction=BUY, execution_price=order.execution_price)

            limit_order.blocked_balance = order.blocked_balance

            self.orders_list.append(limit_order)

            is_executed = True

        elif self.current_klines[order.asset_name][order.timeframe].get_average_price() >= order.stop_price and order.direction == SELL:  # noqa

            limit_order = LimitOrder(order_type=LIMIT, quantity=order.quantity, asset_name=order.asset_name,
                                     direction=SELL, execution_price=order.execution_price)

            limit_order.blocked_balance = order.blocked_balance

            self.orders_list.append(limit_order)

            is_executed = True

        if is_executed:
            self.orders_list.remove(order)

        return is_executed

    def __process_OCO_order(self, order: OcoOrder):
        pass

    def __execute_order(self, order: MarketOrder):

        logger.debug(f'Order {order.order_id} executed')

        logger.debug(f'{order.execution_price, order.direction}')

        price = self.current_klines[order.asset_name][order.timeframe].get_average_price()

        if order.direction == BUY:

            trade = self.user.account_balance - order.quantity * price * (1+self.comission)  # noqa
            self.user.account_balance = trade
            logger.debug(self.user.asset_balance)
            self.user.asset_balance[order.asset_name] += order.quantity

        if order.direction == SELL:

            trade = self.user.asset_balance[order.asset_name] - order.quantity
            self.user.asset_balance = trade
            self.user.account_balance += order.quantity * price * (1-self.comission)  # noqa
