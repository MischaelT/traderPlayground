import asyncio
from datetime import datetime
from typing import List, Tuple, Union

from data.choices import BUY, SELL
from data.db import get_session
from data.models import Balance, BaseOrder, Kline, User
from utils.logger import logger
from data.choices import AssetType, TransactionType


class DemoExchange:
    def __init__(self, user_id: int, multiplier: float = 1, commission: float = 0.1, last_used_timestamp: int = None):
        self.user_id = user_id
        self.is_running = False
        self.last_activity = datetime.now()
        self.multiplier = multiplier
        self.commission = commission
        self.current_time = last_used_timestamp
        self.lock = asyncio.Lock() 
        self.update_data_event = asyncio.Event()


    @property
    def commission(self) -> float:
        return self._commission

    @commission.setter
    def commission(self, value: float):
        self._commission = value
        logger.info(f"Commission set to {value}")

    @property
    def multiplier(self) -> float:
        return self._multiplier

    @multiplier.setter
    def multiplier(self, value: float):
        self._multiplier = value

    def place_order(self, user: User,  order: BaseOrder) -> dict:
        """
        Place an order in the session and commit it to the database.

        Parameters:
            order (BaseOrder): The order to be placed.

        Returns:
            dict: A message confirming the order placement.
        """

        order_is_placed, message = self.__place_order(user, order)

        if not order_is_placed:
            return message

        return {"message": f"Order placed: {order.id}"}


    def get_order_by_id(self, user_id, order_id: int=None) -> Tuple[Union[List[BaseOrder], BaseOrder, None], dict]:
        session = get_session()

        if not order_id:
            orders = session.query(BaseOrder).filter_by(user_id=user_id)
            return orders, {'message': f"Retrieved all orders"}

        order = session.query(BaseOrder).filter_by(user_id=user_id, id=order_id).first()
        if not order:
            logger.warning(f"No order found with ID: {order_id}")
            return None, {'message': f"No order found with ID: {order_id}"}
        logger.info(f"Retrieved order by ID: {order.__dict__}")
        return order, {}


    def cancel_order_by_id(self, order_id: int) -> Tuple[bool, dict]:
        session = get_session()
        order = session.query(BaseOrder).filter_by(id=order_id).first()
        if not order:
            session.delete(order)
            session.commit()
            logger.warning(f"No order found with ID: {order_id}")

            logger.info(f"Order canceled with ID: {order_id}")
            return False, {'message': f"No order found with ID: {order_id}"}
        return True, {'message': f"Cancelled order with ID: {order_id}"}

    def get_orders_by_user_id(self, user_id: int) -> List[BaseOrder]:
        session = get_session()

        user_orders = session.query(BaseOrder).filter_by(id=user_id).all()
        logger.info(f"Retrieved orders by user ID: {user_id}")
        return user_orders

    def get_balance(self, user_id: int, asset_name: Union[str, None] = None) -> Tuple[Union[float, dict, None], dict]:
        session = get_session()

        if not asset_name:
            balance_entries = session.query(Balance).filter_by(user_id=user_id).all()
            balances = {entry.asset_name: entry.amount for entry in balance_entries}
            logger.info(f"Retrieved all balances for user ID {user_id}")
            return balances, {}

        balance_entry = session.query(Balance).filter_by(id=user_id, asset_name=asset_name).first()

        if not balance_entry:
            logger.warning(f"No balance found for user ID {user_id} and asset {asset_name}")
            return None, {'message': f'No balance found for user ID {user_id} and asset {asset_name}'}
        
        return balance_entry.amount, {}

    async def data_updater(self):
        """
        Updates data at specified intervals.
        """
        while self.is_running:
            await asyncio.sleep(1 / self.multiplier)
            async with self.lock:
                session = get_session()
                self.current_time = datetime.now()
                self.current_time += 1
                self.last_activity = datetime.now()
                self.update_data_event.set()
            logger.info(f"Fetched data for user {self.user_id}, current time: {self.current_time}")

    async def order_resolver(self):
        """
        Resolves orders based on updated data.
        """
        while self.is_running:
            await self.update_data_event.wait()
            async with self.lock:
                self.update_data_event.clear()
                self.resolve_orders()
                self.last_activity = datetime.now()
                logger.info(f"Resolved orders for user {self.user_id}, current time: {self.current_time}")

    def resolve_orders(self):
        """
        Resolves orders based on updated data for the stored user ID.
        """
        # Logic to manage orders after data update
        pass

    def start(self):
        """
        Starts the exchange for a specific user.

        """

        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self.data_updater())
            asyncio.create_task(self.order_resolver())
            logger.info(f"Exchange started for user {self.user_id}")

    def stop(self):
        """Stops the exchange."""
        self.is_running = False
        logger.info("Exchange stopped")


    def __place_order(self, user: User, order: BaseOrder) -> bool:
        """
        Checks whether the transaction can be executed based on the provided balance.

        Args:
        - balance (float): Current balance.
        - direction (str): Type of transaction ('BUY' or 'SELL').
        - quantity (int): Quantity of assets involved in the transaction.
        - price (float): Price of the asset.

        Returns:
        bool: True if the balance after the transaction is positive, False otherwise.
        """
        target_asset = order.target_asset
        base_asset = order.base_asset

        user_balance = user.balances[base_asset]

        if order.direction == BUY:
            balance = user.balances[base_asset] - order.quantity * order.execution_price * (1 + self.commission)
        elif order.direction == SELL:
            balance = user.balances[target_asset] - order.quantity
        
        if balance < 0:
            return False, {'message': 'Not enough funds'}

        session = get_session()
        session.add(order)
        session.add(user)
        session.commit()

        logger.info(f"Order placed: {order.id} for user: {user.id}")


        return True, {'message': 'order was placed sussessfully'}




    # def __manage_orders(self):

    #     logger.info('Managing orders...')

    #     for order in self.orders_list:

    #         if order.order_type == MARKET:
    #             self.__process_market_order(order)

    #         elif order.order_type == LIMIT:
    #             self.__process_limit_order(order)

    #         elif order.order_type == STOP_LIMIT:
    #             self.__process_stopLimit_order(order)

    #         elif order.order_type == OCO:
    #             self.__process_OCO_order(order)

    # def __block_balance(self, user: User, order: BaseOrder):

    #     if order.direction == SELL:
    #         order.blocked_balance = order.quantity
    #         self.user.asset_balance[order.asset_name] -= order.blocked_balance
    #     elif order.direction == BUY:
    #         order.blocked_balance = order.quantity * order.execution_price * (1 + self.comission)
    #         self.user.account_balance -= order.blocked_balance

    # def __unblock_balance(self, order: Union[LimitOrder, StopLimitOrder, OcoOrder]):

    #     if order.direction == SELL:

    #         self.user.asset_balance[order.asset_name] += order.blocked_balance

    #     elif order.direction == BUY:

    #         self.user.account_balance += order.blocked_balance

    # def __process_market_order(self, order: MarketOrder):
    #     logger.info('Market order processed')
    #     self.__execute_order(order)

    #     self.orders_list.remove(order)

    # def __process_limit_order(self, order: LimitOrder):

    #     is_executed = False
    #     logger.info('Limit order processed')

    #     if self.current_klines[order.asset_name][order.timeframe].get_average_price() <= order.execution_price and order.direction == BUY:  # noqa

    #         self.user.account_balance += order.blocked_balance

    #         market_order = MarketOrder(direction=order.direction, quantity=order.quantity,
    #                                    asset_name=order.asset_name, execution_price=order.execution_price,
    #                                    order_type=MARKET)

    #         self.__execute_order(market_order)

    #         is_executed = True

    #     elif self.current_klines[order.asset_name][order.timeframe].get_average_price() >= order.execution_price and order.direction == SELL:  # noqa

    #         self.user.asset_balance += order.blocked_balance

    #         market_order = MarketOrder(direction=order.direction, quantity=order.quantity,
    #                                    asset_name=order.asset_name, execution_price=order.execution_price,
    #                                    order_type=MARKET)

    #         self.__execute_order(market_order)

    #         is_executed = True

    #     if is_executed:
    #         self.orders_list.remove(order)

    #     return is_executed

    # def __process_stopLimit_order(self, order: StopLimitOrder):
    #     logger.info('StopLimit order processed')
    #     is_executed = False

    #     if self.current_klines[order.asset_name][order.timeframe].get_average_price() <= order.stop_price and order.direction == BUY:  # noqa

    #         limit_order = LimitOrder(order_type=LIMIT, quantity=order.quantity, asset_name=order.asset_name,
    #                                  direction=BUY, execution_price=order.execution_price)

    #         limit_order.blocked_balance = order.blocked_balance

    #         self.orders_list.append(limit_order)

    #         is_executed = True

    #     elif self.current_klines[order.asset_name][order.timeframe].get_average_price() >= order.stop_price and order.direction == SELL:  # noqa

    #         limit_order = LimitOrder(order_type=LIMIT, quantity=order.quantity, asset_name=order.asset_name,
    #                                  direction=SELL, execution_price=order.execution_price)

    #         limit_order.blocked_balance = order.blocked_balance

    #         self.orders_list.append(limit_order)

    #         is_executed = True

    #     if is_executed:
    #         self.orders_list.remove(order)

    #     return is_executed

    # def __process_OCO_order(self, order: OcoOrder):
    #     pass

    # def __execute_order(self, order: MarketOrder):

    #     logger.debug(f'Order {order.order_id} executed')

    #     logger.debug(f'{order.execution_price, order.direction}')

    #     price = self.current_klines[order.asset_name][order.timeframe].get_average_price()

    #     if order.direction == BUY:

    #         trade = self.user.account_balance - order.quantity * price * (1+self.comission)  # noqa
    #         self.user.account_balance = trade
    #         logger.debug(self.user.asset_balance)
    #         self.user.asset_balance[order.asset_name] += order.quantity

    #     if order.direction == SELL:

    #         trade = self.user.asset_balance[order.asset_name] - order.quantity
    #         self.user.asset_balance = trade
    #         self.user.account_balance += order.quantity * price * (1-self.comission)  # noqa