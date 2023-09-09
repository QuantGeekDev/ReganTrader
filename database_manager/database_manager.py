from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, select, insert, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet
import json
import logging

logging.basicConfig(level=logging.DEBUG)
KEY = b'gkqJ7l5FqJvqe7MqaQSKG5Pl2KZvj2ho5Vgbv4E6UJQ='

Base = declarative_base()


# Define table classes
class ConnectionSettings(Base):
    __tablename__ = 'connection_settings'
    key = Column(String, primary_key=True)
    value = Column(Text)


class BotSettings(Base):
    __tablename__ = 'bot_settings'
    key = Column(String, primary_key=True)
    value = Column(Text)


class SharedStrategySettings(Base):
    __tablename__ = 'shared_strategy_settings'
    key = Column(String, primary_key=True)
    value = Column(Text)


class UserStrategies(Base):
    __tablename__ = 'user_strategies'
    id = Column(Integer, primary_key=True)
    strategy_name = Column(String, nullable=False)
    is_purchased = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)


class StrategySettings(Base):
    __tablename__ = 'strategy_settings'
    strategy_name = Column(String, primary_key=True)
    parameters = Column(Text)


class DatabaseManager:
    def __init__(self, db_path='sqlite:///trading_bot.db'):
        self.engine = create_engine(db_path, echo=True)
        Base.metadata.create_all(self.engine)

    def _encrypt(self, data):
        fernet = Fernet(KEY)
        data = json.dumps(data)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()

    def _decrypt(self, encrypted_data):
        fernet = Fernet(KEY)
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted_data.decode())

    def insert_or_update_record(self, table_class, key, value):
        try:
            value = self._encrypt(value)
            with self.engine.begin() as connection:
                stmt = (
                    update(table_class)
                    .where(table_class.key == key)
                    .values(value=value)
                    .execution_options(synchronize_session="fetch")
                )

                if connection.execute(stmt).rowcount == 0:
                    connection.execute(insert(table_class).values(key=key, value=value))

            logging.info(f"Record {key} in {table_class.__tablename__} updated successfully.")

        except SQLAlchemyError as e:
            logging.error(f"Error in insert_or_update_record: {e}")
            raise

    def get_record(self, table_class, key):
        try:
            with self.engine.begin() as connection:
                stmt = select(table_class.value).where(table_class.key == key)
                result = connection.execute(stmt)
                row = result.fetchone()

                return self._decrypt(row[0]) if row is not None else None

        except SQLAlchemyError as e:
            logging.error(f"Error in get_record: {e}")
            raise

