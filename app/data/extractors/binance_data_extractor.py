import asyncio

import requests
from data.choices import BTC, D1, ETH, H1, H4
from data.extractors.base_data_extractor import BaseDataExtractor
from utils.config import DATE_FROM, DATE_TO
from utils.logging import logger


class BinanceDataExtractor(BaseDataExtractor):

    def __init__(self) -> None:

        self.tickers = {'BTCUSDT': BTC,
                        'ETHUSDT': ETH,}

        self.timeframes = {
            '1h': H1,
            '4h': H4,
            '1d': D1,
        }

        super().__init__()

    async def initialize_db(self):        

        from_ = DATE_FROM
        to = DATE_TO

        periods = self.__set_up_periods(from_, to)
        h1_periods = periods['h1']
        h4_periods = periods['h4']

        tasks = []

        for ticker in self.tickers:

            from_ = 1624233600000
            to = 1655769600000

            tasks.append(self.__get_1d_data(from_, to, ticker))

            for i in range(1, len(h1_periods)):

                from_ = h1_periods[i-1]
                to = h1_periods[i]
                tasks.append(self.__get_1h_data(from_, to, ticker))

            for i in range(1, len(h4_periods)):

                from_ = h4_periods[i-1]
                to = h4_periods[i]
                tasks.append(self.__get_4h_data(from_, to, ticker))

        await asyncio.gather(*tasks)

    def __set_up_periods(self, from_, to):

        h1_periods = []
        time = from_

        h1_periods.append(time)

        while True:

            time += 36000*500

            if time > to:
                break
            else:
                h1_periods.append(time)

        h1_periods.append(to)

        h4_periods = []
        time = from_

        h4_periods.append(time)

        while True:

            time += 3600000*4*500

            if time > to:
                break
            else:
                h4_periods.append(time)

        h4_periods.append(to)

        result = {'h1': h1_periods, 'h4': h4_periods}

        return result

    async def __get_1h_data(self, from_, to, ticker):

        timeframe = H1

        data = self._get_historical_data(ticker=ticker, timeframe=timeframe, from_=from_, to=to)
        self._save_historical_data(klines=data, ticker=self.tickers[ticker], timeframe=timeframe)

    async def __get_4h_data(self, from_, to, ticker):

        timeframe = H4

        data = self._get_historical_data(ticker=ticker, timeframe=timeframe, from_=from_, to=to)
        self._save_historical_data(klines=data, ticker=self.tickers[ticker], timeframe=timeframe)

    async def __get_1d_data(self, from_, to, ticker):

        timeframe = D1

        data = self._get_historical_data(ticker=ticker, timeframe=timeframe, from_=from_, to=to)
        self._save_historical_data(klines=data, ticker=self.tickers[ticker], timeframe=timeframe)

    def _get_historical_data(self, ticker, timeframe, from_, to):

        """
            Connects to API, get historical data by given symbol for given period of time

        Args:
            symbol (str): represents name of asset
            timeframe (str): timeframe of data (15m, 1h, 1d, 1w etc)
            from_date (int): timetamps in seconds
            to_date (int): timestamp in seconds
        """

        url = ' https://api.binance.com/api/v3/klines'

        params = {
            'symbol': ticker,
            'interval': timeframe,
            'startTime': from_,
            'endTime': to,
            # 'limit': 999,
        }

        data = requests.get(url, params).json()

        return data

    def _save_historical_data(self, klines, ticker: str, timeframe: str):

        # logger.debug(klines)

        for kline in klines:

            kline = list(kline)
            logger.debug(kline)

            kline[0] = int(kline[0]/1000)

            for i in range(1, 6):
                kline[i] = round(float(kline[i]), 2)

            params = (kline[0], kline[1], kline[2], kline[3], kline[4], kline[5], timeframe,)

            logger.debug(params)

            self.manager.push_data(params=params, table_name=ticker)
