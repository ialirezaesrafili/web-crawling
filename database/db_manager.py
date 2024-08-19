from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import logging


# Setup logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_url='sqlite:///cars.db'):
        self.engine = create_engine(db_url, echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def get_session(self):
        return self.Session()

    def close_session(self):
        self.Session.remove()
