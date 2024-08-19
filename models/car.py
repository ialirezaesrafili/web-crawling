from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255))
    time = Column(String(50))
    year = Column(String(50))
    mileage = Column(String(50))
    location = Column(String(255))
    description = Column(Text)
    image = Column(Text)
    modified_date = Column(String(50))

    def __repr__(self):
        return f"<Car(title='{self.title}', year='{self.year}', location='{self.location}')>"
