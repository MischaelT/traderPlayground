import csv
from datetime import datetime
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.data.models import Balance, Base, BaseOrder, ExchangeInstance, Kline, LimitOrder, MarketOrder, OcoOrder, StopLimitOrder, User
from app.utils.logger import logger



def get_engine():
   return create_engine('sqlite:///playground.db')


def initialize_database():
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        create_tables(engine)
        return engine
    except Exception as e:
        logger.exception(f"Failed to initialize database: {str(e)}")
        raise

def create_tables(engine):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    tables_to_create = [User, BaseOrder, LimitOrder, MarketOrder, OcoOrder, StopLimitOrder, Kline, ExchangeInstance, Balance]
    for table in tables_to_create:
        if table.__tablename__ not in existing_tables:
            table.metadata.create_all(engine)
            logger.info(f"Table {table.__tablename__} created.")
        else:
            logger.info(f"Table {table.__tablename__} already exists.")

def get_session():
    engine = get_engine()
    try:
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        logger.exception(f"Failed to create session: {str(e)}")
        raise



def create_kline(session, currency, file_path):
    print(file_path)
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            kline = Kline(
                currency_name=currency,
                timestamp=datetime.strptime(row['Date'], '%Y-%m-%d'),
                open_price=float(row['Open']),
                high_price=float(row['High']),
                low_price=float(row['Low']),
                close_price=float(row['Close']),
                volume=float(row['Volume'])
            )
            session.add(kline)
        session.commit()


def initialize_data():
    session = get_session()
    
    # Check if Kline table is empty
    if not session.query(Kline).first():
        folder_path = os.path.join(os.getcwd(), 'app', 'data', 'data' )  # Update this with your folder path
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                currency = filename[:-4]  # Extract currency name from the filename
                file_path = os.path.join(folder_path, filename)
                create_kline(session, currency, file_path)

    session.close()

initialize_database()

initialize_data()
