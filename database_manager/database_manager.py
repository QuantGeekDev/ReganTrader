import logging
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, Boolean, Text, select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError

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
        try:
            with self.engine.connect() as connection:
                connection.execute(table.insert(), data)
        except SQLAlchemyError as e:
            logging.error(f"Error inserting data into {table_name}: {e}")
            raise

    def store_user_config(self, api_key, api_secret, paper):
        encrypted_key = self.encrypt(api_key)
        encrypted_secret = self.encrypt(api_secret)
        self.delete_user_config()
        try:
            with self.engine.connect() as connection:
                connection.execute(insert(self.user_config),
                                   {'api_key': encrypted_key, 'api_secret': encrypted_secret, 'paper': int(paper)})
        except SQLAlchemyError as e:
            logging.error(f"Error storing user config: {e}")
            raise

    def delete_user_config(self):
        try:
            with self.engine.connect() as connection:
                connection.execute(delete(self.user_config))
        except SQLAlchemyError as e:
            logging.error(f"Error deleting user config: {e}")
            raise

    def retrieve_user_config(self):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(select([self.user_config]))
                row = result.fetchone()
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user config: {e}")
            raise

        if row is None:
            return None, None, False

        encrypted_key, encrypted_secret, paper = row
        decrypted_key = self.decrypt(encrypted_key)
        decrypted_secret = self.decrypt(encrypted_secret)
        return decrypted_key, decrypted_secret, bool(paper)

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
