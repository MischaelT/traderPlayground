from fastapi import FastAPI
from routers import auth, exchange_management, trade_management

# if __name__ == '__main__':

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(exchange_management.router, prefix="/playground/exchange")
app.include_router(trade_management.router, prefix="/playground/exchange/trade")

    # @app.get("/openapi.json")
    # async def get_openapi():
    #     return app.openapi()