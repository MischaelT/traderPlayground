from abc import ABC, abstractmethod

from data.postgres import PostgresDB


class BaseDataExtractor(ABC):

    def __init__(self) -> None:
        self.manager = PostgresDB()

    @abstractmethod
    async def initialise_db(self):
        """
            Method that makes asyncio tasks for gathering data ffrom DB
        """

        pass

    @abstractmethod
    def _get_historical_data(self):
        """
            Method that takes data from API
        """

        pass

    @abstractmethod
    def _save_historical_data(self): 
        """
            Method that save data to DB
        """

        pass

