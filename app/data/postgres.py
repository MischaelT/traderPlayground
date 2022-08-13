import logging
from typing import List

import pandas as pd
import psycopg2
from psycopg2 import sql
from data.consts import SUPPORTED_LIST

from utils.config import (POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD,
                          POSTGRES_PORT, POSTGRES_USER)
from utils.logging import logger


class PostgresDB:

    """
        Class provides access to postgres database
    """

    def __init__(self) -> None:

        super().__init__()

        self.initialize_tables(SUPPORTED_LIST)

    def initialize_tables(self, tables_names: list):

        """
            Method initialises tables from given list of names

        Args:
            tables_names (list): list of names
        """

        for name in tables_names:
            self._create_asset_table(name)

    def get_data(self, request_text: str, params: tuple) -> list:

        """
            Method returns data from database

        Returns:
            list(tuple): requested data
        """

        return self._read(request_text, params)

    def push_data(self, params: tuple, table_name) -> None:

        """
            Method pushes data to database
        """

        query = sql.SQL(''' INSERT INTO {table}
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ''').format(table=sql.Identifier(table_name))

        self._write(query, params)

    def query_to_dataframe(self, query_result: list) -> pd.DataFrame:

        """
        Returns pandas dataframe from query result

        """

        columns = ('unix_time', 'open', 'high', 'low', 'close', 'volume', 'timeframe')
        df = pd.DataFrame(query_result, columns=columns)

        return df

    def get_kline_by_time(self, time: int, table_name: str, timeframe: str) -> tuple:

        """
        Method returns a kline with specific time

        Returns:
            tuple: database row
        """

        query = sql.SQL(''' SELECT * FROM {table}
                            WHERE (unix_time=%s) AND (timeframe=%s)
                        ''').format(table=sql.Identifier(table_name))

        params = (time, timeframe)

        try:
            row = self._read(query, params)[0]
        except Exception as e:
            row = (1, 1, 1, 1, 1, 1, 1, 1)
            logging.debug(e)

        return row

    def get_latest_klines(self, number: int, table_name: str, timeframe: str) -> List[tuple]:

        """
        Method returns latest n klines

        Returns:
            tuple: database row
        """

        query = sql.SQL(''' SELECT * FROM {table}
                            WHERE (timeframe=%s)
                            ORDER BY unix_time DESC
                            LIMIT %s
                        ''').format(table=sql.Identifier(table_name))

        params = (timeframe, number,)

        row = self._read(query, params)

        return row

    def get_latest_by_time(self, number: int, time: int, table_name: str, timeframe: str) -> List[tuple]:

        """
        Method returns latest n klines before specific time

        Returns:
            tuple: database row
        """

        query = sql.SQL(''' SELECT * FROM {table}
                            WHERE (unix_time<%s) AND (timeframe=%s)
                            ORDER BY unix_time DESC
                            LIMIT %s
                        ''').format(table=sql.Identifier(table_name))

        params = (time, timeframe, number,)

        row = self._read(query, params)

        return row

    def _create_asset_table(self, table_name: str) -> None:

        """
            Method create table with given name if it have not already exists
        """

        connection = self._make_connection()

        try:

            cursor = connection.cursor()

            create_table_query = sql.SQL('''CREATE TABLE IF NOT EXISTS {table} (
                                            UNIX_TIME       SERIAL                       NOT NULL,
                                            OPEN            REAL                         NOT NULL,
                                            HIGH            REAL                         NOT NULL,
                                            LOW             REAL                         NOT NULL,
                                            CLOSE           REAL                         NOT NULL,
                                            VOLUME          REAL                         NOT NULL,
                                            TIMEFRAME       TEXT                         NOT NULL

                                ); ''').format(table=sql.Identifier(table_name))

            cursor.execute(create_table_query)

            connection.commit()

        except (Exception) as exception:
            logging.exception(f'There was a problem during creating table : {str(exception)}')

        finally:
            if connection:
                cursor.close()
                connection.close()

    def _make_connection(self):

        """
            Method connecting to database using autentication data from config.py

        Returns:
           connection: Connection object
        """

        try:
            connection = psycopg2.connect(
                                        user=POSTGRES_USER,
                                        password=POSTGRES_PASSWORD,
                                        host=POSTGRES_HOST,
                                        port=POSTGRES_PORT,
                                        database=POSTGRES_DB
                                        )

        except (Exception) as exception:
            logging.exception(f'There was a problem during creating connection: {str(exception)}')

        return connection

    def _write(self, query: str, params: tuple) -> None:

        """
        Method writes data to database.

        Args:
            query (str): SQL query
            params (tuple): parameters for inserting to query
        """

        connection = self._make_connection()

        try:

            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()

        except Exception as exception:
            logging.exception(f'There was a problem during writing: {str(exception)}')

        finally:
            if connection:
                cursor.close()
                connection.close()

    def _read(self, query: str, params: tuple) -> list:

        """
            Method receives data from database

        Returns:
            list: list of tuples with requested data
        """

        connection = self._make_connection()

        record = []

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            record = cursor.fetchall()

        except Exception as exception:
            logging.exception(f'There was a problem during reading: {str(exception)}')

        finally:
            if connection:
                cursor.close()
                connection.close()

        return record

    def initiate_tedtBD(self):

        one_tick = 3600*24
        unix_time = 1612051200

        for i in range(200):

            unix_time += one_tick

            logger.debug(i)

            if i < 25:
                price = 100
            elif i > 25 and i <= 50:
                price = 50
            elif i > 50 and i <= 75:
                price = 25
            elif i > 75 and i <= 100:
                price = 50
            elif i > 100 and i <= 125:
                price = 100
            elif i > 125 and i <= 150:
                price = 50
            elif i > 150 and i <= 175:
                price = 25
            elif i > 175:
                price = 50

            params = (unix_time, 0, 0, 0, price, 0, '1d',)

            query = '''INSERT INTO test_data (unix_time, open, high, low, close, volume, timeframe)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)'''

            self.__manager.push_data(params=params, query=query)