
from app.data.db import get_session
from app.data.models import User
from app.routers.mics import secured, verify_api_key

from app.extensions import exchanges_manager
from fastapi import APIRouter, Depends, HTTPException, Request


router = APIRouter()

@secured
@router.post("/start_exchange")
async def start_exchange(api_key: str):

    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")

    ecxchange = exchanges_manager.start_exchange(user)

    if ecxchange: 
        return {"message": f'Exchange is up for user: {user.api_key}'}
    return {"message": f'Problem occured while getting exchange for user: {user.api_key}'}

@secured
@router.post("/stop_exchange")
async def stop_exchange(api_key: str):

    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")

    message = exchanges_manager.stop_exchange(user)
    return {"message": message}
    
@secured
@router.post("/set_multiplier")
async def set_multiplier(api_key: str, multiplier: float):

    session = get_session()
    user = session.query(User).filter_by(api_key=api_key).first()

    if not user:
        raise HTTPException(status_code=403, detail="Provide valid API key")
    
    message = exchanges_manager.set_multiplier(user, multiplier)
    return {"message": message}
