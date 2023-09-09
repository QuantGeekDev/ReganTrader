import logging
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, Boolean, Text, select, insert, delete, \
    update
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.DEBUG)
KEY = b'gkqJ7l5FqJvqe7MqaQSKG5Pl2KZvj2ho5Vgbv4E6UJQ='


class DatabaseManager:
    def __init__(self, db_path='sqlite:///trading_bot.db'):
        self.engine = create_engine(db_path, echo=True)
        self.metadata = MetaData()

        # Connection_Settings Table Definition
        self.connection_settings = Table('connection_settings', self.metadata,
                                         Column('key', String, primary_key=True),
                                         Column('value', Text))
        # Bot_Settings Table Definition
        self.bot_settings = Table('bot_settings', self.metadata,
                                  Column('key', String, primary_key=True),
                                  Column('value', Text))
        # Shared_Stratgy_Settings Table Definition
        self.shared_strategy_settings = Table('shared_strategy_settings', self.metadata,
                                              Column('key', String, primary_key=True),
                                              Column('value', Text))
        # User_Strategies Table Definition
        self.user_strategies = Table('user_strategies', self.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('strategy_name', String, nullable=False),
                                     Column('is_purchased', Boolean, nullable=False, default=False),
                                     Column('is_active', Boolean, nullable=False, default=False))
        # Strategy_Settings Table Definition
        self.strategy_settings = Table('strategy_settings', self.metadata,
                                       Column('strategy_name', String, primary_key=True),
                                       Column('parameters', Text))
        self.metadata.create_all(self.engine)

    def create_table(self, table_name):
        try:
            table = Table(table_name, self.metadata,
                          Column('timestamp', Text, primary_key=True),
                          Column('data', Text))
            table.create(self.engine, checkfirst=True)
        except SQLAlchemyError as e:
            logging.error(f"Error creating table {table_name}: {e}")
            raise

    def select_data(self, table_name, start=None, end=None):
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        query = select([table]).where(table.c.timestamp.between(start, end))
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()

    def insert_data(self, table_name, data):
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        logging.info(f"Inserting data into {table_name}")
        logging.debug(f"Data: {data}")
        try:
            with self.engine.connect() as connection:
                connection.execute(table.insert(), data)
            logging.info(f"Data inserted successfully")
        except SQLAlchemyError as e:
            logging.error(f"Error inserting data into {table_name}: {e}")
            raise

    def retrieve_configuration(self, key, table_name):
        with self.engine.begin() as connection:
            table = self.get_table(table_name)
            s = select(table.c.value).where(table.c.key == key)  # Select the 'value' column
            result = connection.execute(s)
            row = result.fetchone()
            return row[0] if row is not None else None

    def insert_configuration(self, key, value, table_name):
        logging.info(f"Inserting configuration {key} into {table_name}")
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        try:
            with self.engine.begin() as connection:
                # Update the configuration if it exists, else insert
                update_stmt = (
                    update(table)
                    .where(table.c.key == key)
                    .values(value=value)
                    .execution_options(synchronize_session="fetch")
                )

                if connection.execute(update_stmt).rowcount == 0:
                    connection.execute(insert(table).values(key=key, value=value))

                logging.info(f"Configuration for key {key} in {table_name} updated successfully")
        except SQLAlchemyError as e:
            logging.error(f"Error inserting/updating configuration: {e}")
            raise
        except Exception as e:
            logging.error(f"Unhandled error in insert_configuration: {e}")
            raise



    @staticmethod
    def encrypt(data):
        fernet = Fernet(KEY)
        data = data.encode() if isinstance(data, str) else data
        return fernet.encrypt(data).decode()

    @staticmethod
    def decrypt(data):
        fernet = Fernet(KEY)
        data = data.encode() if isinstance(data, str) else data
        return fernet.decrypt(data).decode()
