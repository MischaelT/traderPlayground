from datetime import datetime

from app.data.db import get_session
from app.data.models import User
from fastapi import APIRouter
from app.routers.mics import generate_api_key

router = APIRouter()


@router.post("/generate_api_key")
async def generate_new_api_key():

    new_api_key = generate_api_key()
 
    session = get_session()
    new_user = User(creation_date = datetime.now(), api_key = new_api_key)
    session.add(new_user)
    session.commit()

    return {"message": "New API key generated", "api_key": new_api_key}
