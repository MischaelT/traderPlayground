from app.data.db import get_session
from app.data.models import User
from app.extensions import exchanges_manager
from fastapi import APIRouter, HTTPException
from app.playground.order_factory import OrderFactory
from app.routers.mics import secured
from app.routers.models import Order

router = APIRouter()

@secured
@router.post("/place_order")
async def place_order(order_data: Order, api_key: str):
    
    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    order, message = OrderFactory.create_order(order_data)
    if not order:
        return message 
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message

    message = exchange.place_order(order)

    return message


@secured
@router.get("/orders")
async def get_open_orders(api_key: str):
    
    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message
    
    orders, message = exchange.get_order_by_id(user_id=user.id)

    return {"message": f"Open orders retrieved: {orders}"}

@secured
@router.get("/orders/{order_id}")
async def get_open_orders(order_id, api_key: str):
    
    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message
    
    order, message = exchange.get_order_by_id(user_id=user.id, order_id=order_id)

    if not order:
        return message

    return {"message": "Open orders retrieved"}


@secured
@router.post("/cancel_order/{order_id}")
async def cancel_order(api_key: str, order_id: str):
    
    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message

    return {"message": f"Order {order_id} canceled"}

@secured
@router.get("/asset_balance")
async def get_asset_balance(api_key: str):

    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message
    
    balances, message = exchange.get_balance(user_id=user.id)

    return {"message": f"Asset balance retrieved {balances}"}


@secured
@router.get("/asset_balance/{asset_name}")
async def get_asset_balance(api_key: str):

    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message
    
    balance, message = exchange.get_balance(user_id=user.id)

    return {"message": f"Asset balance retrieved: {balance}"}

@secured
@router.get("/statistics")
async def get_statistics(api_key: str):
    
    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    exchange, message = exchanges_manager.start_exchange(user)
    if not exchange:
        return message

    return {"message": "Statistics retrieved"}
