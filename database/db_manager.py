from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
from models.car import Base

# Setup logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_url='sqlite:///cars.sqlite'):
        self.engine = create_engine(db_url, echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close_session(self):
        self.Session.remove()

    def add_instance(self, model_class, data_dict):
        session = self.get_session()
        try:
            instance = model_class(**data_dict)
            session.add(instance)
            session.commit()
            logger.info(f"Added {instance} to the database.")
        except Exception as e:
            logger.error(f"Failed to add {data_dict} to the database: {e}")
            session.rollback()
        finally:
            session.close()
