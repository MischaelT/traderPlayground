from data.choices import BTC, ETH

from exchange_imitator.imitator import Imitator

from utils.logging import logger


user_balance = 100000
trading_list = [BTC, ETH]

exchange_imitator = Imitator(user_balance=user_balance,
                             trading_list=trading_list,
                             ticks_for_test=200,
                             comission=0.001,
                             multi_timeframes=False)

if __name__ == '__main__':

    while True:
        exchange_imitator.check_connection()
        kline = exchange_imitator.get_kline(BTC)
        logger.info(kline)
