from dataclasses import dataclass, fields
from data.models import LimitOrder, MarketOrder, OcoOrder, StopLimitOrder


BTC = "btc"
ETH = "eth"

BUY = 'buy'
SELL = 'sell'

MARKET = 'market'
LIMIT = 'limit'
STOP_LIMIT = 'stop_limit'
OCO = 'oco'


order_classes = {
    MARKET: MarketOrder,
    LIMIT: LimitOrder,
    OCO: OcoOrder,
    STOP_LIMIT: StopLimitOrder
}


@dataclass
class BaseType:
    def find_attribute_by_value(self, search_value):
        for field in fields(self):
            if getattr(self, field.name) == search_value:
                return field.name
        return None

@dataclass
class AssetType(BaseType):
    BTC: str = BTC
    ETH: str = ETH


@dataclass
class TransactionType(BaseType):
    BUY: str = BUY
    SELL: str = SELL

@dataclass
class OrderType(BaseType):
    MARKET: str = MARKET
    LIMIT: str = LIMIT
    STOP_LIMIT: str = STOP_LIMIT
    OCO: str = OCO