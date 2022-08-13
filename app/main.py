from exchange_imitator.imitator import Imitator

from utils.logging import logger


user_balance = 100000
trading_list = []

exchange_imitator = Imitator(user_balance = user_balance,
                             trading_list = trading_list)

if __name__ == '__main__':

    while True:
        exchange_imitator.check_connection()
        kline = exchange_imitator.get_kline()
        logger.info(kline)
