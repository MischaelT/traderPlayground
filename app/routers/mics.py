# Function to generate an API key
from functools import wraps
import secrets

from fastapi import HTTPException

from app.data.db import get_session
from app.data.models import User


def generate_api_key():
    return secrets.token_urlsafe(32)

def verify_api_key(api_key: str):
    session = get_session()
    api_in_db = bool(session.query(User).filter_by(api_key=api_key).first())
    return api_in_db

def secured(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        api_key = kwargs.get("api_key")
        if not verify_api_key(api_key):
            raise HTTPException(status_code=403, detail="Invalid API key")
        return await func(*args, **kwargs)

    return wrapper  