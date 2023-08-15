from fastapi import FastAPI
from playground.api import register_endpoints


if __name__ == '__main__':

    app = FastAPI()

    register_endpoints(app)
