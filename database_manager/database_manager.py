# database_manager.py

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy.exc import SQLAlchemyError
Base = declarative_base()


class ConnectionSettings(Base):
    __tablename__ = 'connection_settings'
    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    api_secret = Column(String)
    paper = Column(Boolean)


class StrategySettings(Base):
    __tablename__ = 'strategy_settings'
    id = Column(Integer, primary_key=True)
    strategy_name = Column(String)
    parameter1 = Column(Integer)
    trading_interval = Column(Integer)
    data_update_interval = Column(Integer)
    start_time = Column(String)
    end_time = Column(String)
    limit = Column(Integer)
    feed = Column(String)
    timeframe = Column(String)

class RiskSettings(Base):
    __tablename__ = 'risk_settings'
    id = Column(Integer, primary_key=True)
    # Add your fields here, for example:
    max_loss = Column(Integer)
    max_trade = Column(Integer)


class DatabaseManagerBase:
    def __init__(self, db_url, model_class):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.model_class = model_class

    def add(self, **kwargs):
        session = self.Session()
        new_instance = self.model_class(**kwargs)
        session.add(new_instance)
        session.commit()

    def get(self, filter_by=None):
        session = self.Session()
        query = session.query(self.model_class)
        if filter_by:
            query = query.filter_by(**filter_by)
        return query.first()

    def update(self, filter_by, **kwargs):
        session = self.Session()
        try:
            instance = session.query(self.model_class).filter_by(**filter_by).first()
            if instance is None:
                logging.error(f"No record found for filter: {filter_by}")
                return
            for key, value in kwargs.items():
                setattr(instance, key, value)
            session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Database error during update: {str(e)}")
            session.rollback()

    def delete(self, filter_by):
        session = self.Session()
        instance = session.query(self.model_class).filter_by(**filter_by).first()
        session.delete(instance)
        session.commit()


class ConnectionSettingsManager(DatabaseManagerBase):
    def __init__(self, db_url):
        super().__init__(db_url, ConnectionSettings)


class StrategySettingsManager(DatabaseManagerBase):
    def __init__(self, db_url):
        super().__init__(db_url, StrategySettings)


class RiskSettingsManager(DatabaseManagerBase):
    def __init__(self, db_url):
        super().__init__(db_url, RiskSettings)
