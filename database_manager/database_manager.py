import logging
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, Boolean, Text, select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
logging.basicConfig(level=logging.DEBUG)
KEY = b'gkqJ7l5FqJvqe7MqaQSKG5Pl2KZvj2ho5Vgbv4E6UJQ='


class DatabaseManager:
    def __init__(self, db_path='sqlite:///trading_bot.db'):
        self.engine = create_engine(db_path, echo=True)
        self.metadata = MetaData()
        self.user_config = Table('user_config', self.metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('api_key', Text, nullable=False),
                                 Column('api_secret', Text, nullable=False),
                                 Column('paper', Boolean, nullable=False, default=False))
        self.config = Table('config', self.metadata,
                            Column('key', String, primary_key=True),
                            Column('value', Text))
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

    def store_user_config(self, api_key: str, api_secret: str, paper: bool):
        try:
            with self.engine.begin() as connection:
                # delete existing config
                connection.execute(delete(self.user_config))
                # insert new config
                connection.execute(insert(self.user_config).values(api_key=self.encrypt(api_key),
                                                                    api_secret=self.encrypt(api_secret),
                                                                    paper=paper))
        except SQLAlchemyError as e:
            logging.error(f"Error storing user config: {e}")
            raise
        except Exception as e:
            logging.error(f"Unhandled error in store_user_config: {e}")
            raise


    def delete_user_config(self):
        try:
            with self.engine.connect() as connection:
                connection.execute(delete(self.user_config))
        except SQLAlchemyError as e:
            logging.error(f"Error deleting user config: {e}")
            raise

    def retrieve_user_config(self):
        logging.info("Retrieving user config")
        try:
            with self.engine.begin() as connection:
                result = connection.execute(
                    select(self.user_config.c.api_key, self.user_config.c.api_secret, self.user_config.c.paper))
                row = result.fetchone()

                if row is None:
                    logging.info("No user config found.")
                    return None, None, False

                logging.debug(f"Retrieved user config: {row}")
                encrypted_key, encrypted_secret, paper = row

                try:
                    decrypted_key = self.decrypt(encrypted_key)
                    decrypted_secret = self.decrypt(encrypted_secret)
                except Exception as e:
                    logging.error(f"Error during decryption: {e}")
                    raise

                logging.info(f"Decrypted user config: {decrypted_key}, {decrypted_secret}, {bool(paper)}")
                return decrypted_key, decrypted_secret, bool(paper)
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user config: {e}")
            raise
        except Exception as e:
            logging.error(f"Unhandled error in retrieve_user_config: {e}")
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


db_manager = DatabaseManager()
