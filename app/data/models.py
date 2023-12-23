from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True,  autoincrement=True)
    creation_date = Column(DateTime)
    api_key = Column(String)

    orders = relationship("BaseOrder", back_populates="user")
    balances = relationship("Balance", back_populates="user")



class BaseOrder(Base):
    __tablename__ = 'base_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(DateTime)
    order_type = Column(String)
    quantity = Column(Integer)
    base_asset = Column(String)
    target_asset = Column(String)
    direction = Column(String)
    execution_price = Column(Float)
    stop_price = Column(Float)
    signal_price = Column(Float)
    blocked_amount = Column(Float)

    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key referencing the User table
    user = relationship("User", back_populates="orders")  # Relationship definition in the Order class


class MarketOrder(BaseOrder):
    __tablename__ = 'market_orders'
    id = Column(Integer, ForeignKey('base_orders.id'), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "market"}


class LimitOrder(BaseOrder):
    __tablename__ = 'limit_orders'
    id = Column(Integer, ForeignKey('base_orders.id'), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "limit"}

class OcoOrder(BaseOrder):
    __tablename__ = 'oco_orders'
    id = Column(Integer, ForeignKey('base_orders.id'), primary_key=True)
    bounded_order_id = Column(Integer)  # Specific to OCO orders
    __mapper_args__ = {"polymorphic_identity": "oco"}

class StopLimitOrder(BaseOrder):
    __tablename__ = 'stop_limit_orders'
    id = Column(Integer, ForeignKey('base_orders.id'), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "stop_limit"}




    discriminator = Column(String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True,  autoincrement=True)
    asset_name = Column(String)
    amount = Column(Float)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="balances")



class Kline(Base):
    __tablename__ = 'klines'

    id = Column(Integer, primary_key=True)
    currency_name = Column(String)
    timestamp = Column(DateTime)
    open_price = Column(Float)
    close_price = Column(Float)
    low_price = Column(Float)
    high_price = Column(Float)
    volume = Column(Float)

class ExchangeInstance(Base):
    __tablename__ = 'exchange_instances'

    id = Column(Integer, primary_key=True,  autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    last_used_timestamp = Column(Integer)
    multiplier = Column(Float)
    commission = Column(Float)
    user = relationship("User")