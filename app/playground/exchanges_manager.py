import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from app.consts import DEFAULT_COMISSION, DEFAULT_MULTIPLIER
from app.data.db import get_session
from app.data.models import ExchangeInstance, User
from app.playground.exchange import DemoExchange
from app.utils.logger import logger


class ExchangesManager:
    def __init__(self):
        self.exchange_instances: Dict[str, DemoExchange] = {0: DemoExchange(user_id=1)}

    async def check_inactive_exchanges(self):
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = datetime.now()
            for user_id, exchange in list(self.exchange_instances.items()):
                if (current_time - exchange.last_activity) > timedelta(minutes=5):
                    exchange.stop()
                    del self.exchange_instances[user_id]
                    logger.info(f"Exchange instance for user {user_id} deleted due to inactivity.")


    def start_exchange(self, user: User) -> Tuple[DemoExchange, dict]:
        """
        Start a new exchange instance for the user or retrieve an existing one from the database.

        Parameters:
            user (User): The user initiating the exchange.

        Returns:
            dict: A message confirming the exchange start or an error message.
        """
        if user.id in self.exchange_instances:
            logger.warning(f"Exchange already active for user {user.id}")
            return self.exchange_instances[user.id], {}

        session = get_session()
        saved_exchange_data = session.query(ExchangeInstance).filter_by(user_id=user.id).first()

        commission = saved_exchange_data.commission if saved_exchange_data else DEFAULT_COMISSION
        multiplier = saved_exchange_data.multiplier if saved_exchange_data else DEFAULT_MULTIPLIER
        last_used_timestamp = saved_exchange_data.last_used_timestamp if saved_exchange_data else None

        try:
            self.exchange_instances[user.id] = DemoExchange(commission=commission,
                                                            multiplier=multiplier,
                                                            last_used_timestamp=last_used_timestamp,
                                                            user_id=user.id)
        except Exception as e:
            logger.exception(f"Error creating exchange for user: {str(e)}")
            return None, {"message": f"Error occurred for user {user.id}"}

        return self.exchange_instances[user.id], {}


    def get_exchange(self, user: User) -> DemoExchange:
        """
        Retrieve an existing exchange instance for the user from the database.

        Parameters:
            user (User): The user initiating the exchange.

        Returns:
            DemoExchange: The existing exchange instance if found, else None.
        """
        if user.id in self.exchange_instances:
            logger.warning(f"Exchange already active for user {user.id}")
            return self.exchange_instances[user.id]

        session = get_session()
        saved_exchange_data = session.query(ExchangeInstance).filter_by(user_id=user.id).first()

        commission = saved_exchange_data.commission if saved_exchange_data else DEFAULT_COMISSION
        multiplier = saved_exchange_data.multiplier if saved_exchange_data else DEFAULT_MULTIPLIER
        last_used_timestamp = saved_exchange_data.last_used_timestamp if saved_exchange_data else None
        try:
            self.exchange_instances[user.id] = DemoExchange(commission=commission,
                                                            multiplier=multiplier,
                                                            last_used_timestamp=last_used_timestamp,
                                                            user_id=user.id)
        except Exception as e:
            logger.exception(f"Error creating exchange for user: {str(e)}")
            return None, {'message': f"Error creating exchange for user: {str(e)}"}
        return self.exchange_instances[user.id], {}


    def start_exchange(self, user: User) -> dict:
        """
        Start a new exchange instance for the user if not found in the database.

        Parameters:
            user (User): The user initiating the exchange.

        Returns:
            dict: A message confirming the exchange start or an error message.
        """
        exchange = self.exchange_instances[user.id]
        
        if exchange:
            return None, f"Exchange already active for user {user.id}"

        exchange = self.get_exchange(user)

        if not exchange:
            exchange = DemoExchange(user_id=user.id)

        self.exchange_instances[user.id] = exchange

        try:
            exchange.start()
        except Exception as e:
            logger.exception(f"Error starting exchange for user: {str(e)}")
            return None, f"Error occurred for user {user.id}"

        return exchange, "Exchange started successfully"

    def stop_exchange(self, user: User) -> Dict[str, Any]:
        """
            Stop the exchange for the given user and save data in the database.

            Parameters:
                user (User): The user for whom the exchange needs to be stopped.
                db (Session): The SQLAlchemy database session.

            Returns:
                dict: A message confirming the exchange stoppage or an error message.
        """
        if user.id not in self.exchange_instances:
            logger.warning(f"No active exchange found for user {user.id}")
            return {"message": f"No active exchange found for user {user.id}"}

        exchange = self.exchange_instances[user.id]
        multiplier = exchange.multiplier
        commission = exchange.commission
        last_activity = exchange.last_activity

        db = get_session()
        # Check if the user already has an existing exchange instance in the database
        existing_exchange = db.query(ExchangeInstance).filter_by(user_id=user.id).first()

        if existing_exchange:
            # Update the existing exchange instance in the database
            existing_exchange.last_used_timestamp = last_activity.timestamp()
            existing_exchange.multiplier = multiplier
            existing_exchange.commission = commission
        else:
            # Create a new exchange instance in the database
            exchange_instance = ExchangeInstance(
                user_id=user.id,
                last_used_timestamp=last_activity.timestamp(),
                multiplier=multiplier,
                commission=commission
            )
            db.add(exchange_instance)

        # Stop the exchange
        exchange.stop()
        del self.exchange_instances[user.id]
        logger.info(f"Exchange stopped for user {user.id}")

        db.commit()  # Commit changes to the database

        return {"message": f"Exchange stopped for user {user.id}"}


    def set_multiplier(self, user: User, multiplier: float) -> dict:
        """
        Set the multiplier for the user's exchange instance.

        Parameters:
            user (User): The user whose exchange's multiplier needs to be set.
            multiplier (float): The multiplier value to be set.

        Returns:
            dict: A message confirming the multiplier change or an error message.
        """
        if user.id not in self.exchange_instances:
            logger.warning(f"No active exchange found for user {user.id}")
            return {"message": f"No active exchange found for user {user.id}"}

        running_exchange = self.exchange_instances[user.id]
        running_exchange.multiplier = multiplier

        session = get_session()
        
        # existing_exchange = session.query(ExchangeInstance).filter_by(user_id=user.id).first()
        # existing_exchange.multiplier = multiplier

        session.commit()

        logger.info(f"Multiplier set to {multiplier} for user {user.id}")
        return {"message": f"Multiplier set to {multiplier} for user {user.id}"}


    def set_commission(self, user: str, commission: float) -> Dict[str, Any]:
        """
        Set the commission for the user's exchange instance.

        Parameters:
            user (str): The user ID whose exchange's commission needs to be set.
            commission (float): The commission value to be set.

        Returns:
            dict: A message confirming the commission change or an error message.
        """
        if user.id not in self.exchange_instances:
            logger.warning(f"No active exchange found for user {user.id}")
            return {"message": f"No active exchange found for user {user.id}"}

        running_exchange = self.exchange_instances[user.id]
        running_exchange.multiplier = commission

        session = get_session()

        existing_exchange = session.query(ExchangeInstance).filter_by(user_id=user.id).first()
        existing_exchange.comission = commission
        session.commit()

        logger.info(f"Commission set to {commission} for user {user.id}")
        return {"message": f"Commission set to {commission} for user {user.id}"}
    
