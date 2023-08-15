from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

import uuid

from typing import Dict
from data.choices import BTC, ETH

from exchange_imitator.exchange import DemoExchange

user_balance = 100000
trading_list = [BTC, ETH]
ticks_for_test=200,
comission=0.001,
multi_timeframes=False
timeframe = '1h'

exchange = DemoExchange(user_balance, trading_list, ticks_for_test, multi_timeframes, timeframe, comission=comission)


class OrderRequest(BaseModel):
    order_direction: str
    ticker: str
    quantity: float
    price: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    timeframe: str

def register_endpoints(app):

    # Create a dictionary to store registered persons and their API keys
    registered_persons = {}

    @app.post("/register")
    async def register_person(name: str, email: str) -> Dict[str, str]:
        # Generate a unique API key
        api_key = str(uuid.uuid4())
        
        # Store the person's information and API key in the dictionary
        registered_persons[api_key] = {"name": name, "email": email}
        
        return {"api_key": api_key}

    @app.get("/get_api_key")
    async def get_api_key(name: str, email: str) -> Dict[str, Optional[str]]:
        # Search for the person's API key based on their name and email
        for api_key, person_info in registered_persons.items():
            if person_info["name"] == name and person_info["email"] == email:
                return {"api_key": api_key}
        
        raise HTTPException(status_code=404, detail="Person not found")

    @app.post("/place_market_order")
    async def place_market_order(order_request: OrderRequest):
        order_id = exchange.place_market_order(
            order_direction=order_request.order_direction,
            ticker=order_request.ticker,
            quantity=order_request.quantity,
            timeframe=order_request.timeframe
        )
        return {"order_id": order_id}

    @app.post("/place_limit_order")
    async def place_limit_order(order_request: OrderRequest):
        order_id = exchange.place_limit_order(
            order_direction=order_request.order_direction,
            ticker=order_request.ticker,
            quantity=order_request.quantity,
            price=order_request.price,
            timeframe=order_request.timeframe
        )
        return {"order_id": order_id}

    @app.post("/place_stoplimit_order")
    async def place_stoplimit_order(order_request: OrderRequest):
        order_id = exchange.place_stopLimit_order(
            order_direction=order_request.order_direction,
            ticker=order_request.ticker,
            quantity=order_request.quantity,
            stop_price=order_request.stop_price,
            limit_price=order_request.limit_price,
            timeframe=order_request.timeframe
        )
        return {"order_id": order_id}

    @app.get("/open_orders")
    async def get_open_orders():
        open_orders = exchange.get_open_orders()
        return {"open_orders": open_orders}
    
    @app.post("/place_OCO_order")
    async def place_OCO_order():
        # Implement your logic here
        return {"message": "OCO order placed"}

    @app.post("/cancel_order/{order_id}")
    async def cancel_order(order_id: str):
        exchange.cancel_order(order_id)
        return {"message": f"Order {order_id} canceled"}

    @app.get("/open_orders")
    async def get_open_orders():
        open_orders = exchange.get_open_orders()
        return {"open_orders": open_orders}

    @app.get("/asset_balance")
    async def get_asset_balance():
        # Implement your logic here
        return {"message": "Asset balance endpoint"}

    @app.get("/statistics")
    async def get_statistics():
        statistics = exchange.get_statistics()
        return {"statistics": statistics}


