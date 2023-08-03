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
        self.user_strategies = Table('user_strategies', self.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('strategy_name', String, nullable=False),
                                     Column('is_purchased', Boolean, nullable=False, default=False),
                                     Column('is_active', Boolean, nullable=False, default=False))

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

#TODO: Implement the is_purchase and is_active bools:
    def set_active_strategy(self, strategy_name):
        logging.info(f"Setting active strategy {strategy_name}")
        self.insert_configuration('active_strategy', strategy_name)

    def get_active_strategy(self):
        logging.info("Retrieving active strategy")
        return self.retrieve_configuration('active_strategy')
    def store_strategy(self, strategy_name: str, is_purchased: bool, is_active: bool):
        try:
            with self.engine.begin() as connection:
                connection.execute(insert(self.user_strategies).values(strategy_name=strategy_name,
                                                                       is_purchased=is_purchased,
                                                                       is_active=is_active))
        except SQLAlchemyError as e:
            logging.error(f"Error storing strategy: {e}")
            raise

    def retrieve_strategy(self, strategy_name: str):
        logging.info(f"Retrieving strategy {strategy_name}")
        try:
            with self.engine.begin() as connection:
                result = connection.execute(select(self.user_strategies.c.is_purchased,
                                                   self.user_strategies.c.is_active)
                                            .where(self.user_strategies.c.strategy_name == strategy_name))
                row = result.fetchone()

                if row is None:
                    logging.info("Strategy not found.")
                    return None, None

                is_purchased, is_active = row

                logging.info(f"Retrieved strategy: {is_purchased}, {is_active}")
                return is_purchased, is_active
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving strategy: {e}")
            raise
    def retrieve_configuration(self, key):
        logging.info(f"Retrieving configuration {key}")
        try:
            with self.engine.begin() as connection:
                result = connection.execute(
                    select(self.config.c.value)
                    .where(self.config.c.key == key))
                row = result.fetchone()

                if row is None:
                    logging.info(f"No configuration found for key: {key}")
                    return None

                logging.debug(f"Retrieved configuration for key {key}: {row[0]}")
                return row[0]
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving configuration: {e}")
            raise
        except Exception as e:
            logging.error(f"Unhandled error in retrieve_configuration: {e}")
            raise

    def insert_configuration(self, key, value):
        logging.info(f"Inserting configuration {key}")
        try:
            with self.engine.begin() as connection:
                # Update the configuration if it exists, else insert
                update_stmt = (
                    update(self.config)
                    .where(self.config.c.key == key)
                    .values(value=value)
                    .execution_options(synchronize_session="fetch")
                )

                if connection.execute(update_stmt).rowcount == 0:
                    connection.execute(insert(self.config).values(key=key, value=value))

                logging.info(f"Configuration for key {key} updated successfully")
        except SQLAlchemyError as e:
            logging.error(f"Error inserting/updating configuration: {e}")
            raise
        except Exception as e:
            logging.error(f"Unhandled error in insert_configuration: {e}")
            raise

    def retrieve_all_configurations(self):
        logging.info("Retrieving all configurations")
        try:
            with self.engine.begin() as connection:
                result = connection.execute(select(self.config.c.key, self.config.c.value))
                rows = result.fetchall()

                if rows is None:
                    logging.info("No configurations found.")
                    return None

                logging.debug(f"Retrieved configurations: {rows}")
                return {row[0]: row[1] for row in rows}
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving configurations: {e}")
            raise
        except Exception as e:
            logging.error(f"Unhandled error in retrieve_all_configurations: {e}")
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
