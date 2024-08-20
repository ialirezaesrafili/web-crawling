import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.car import Car, Base


# Create an in-memory SQLite database for testing
@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope='module')
def create_tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def session(engine, create_tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_car_model_creation(session):
    # Create an instance of Car
    new_car = Car(
        url='https://bama.ir/car-url',
        title='Test Car',
        time='2024-08-19',
        year='2023',
        mileage='5000',
        location='Test City',
        description='A test car description',
        image='car.jpg',
        modified_date='2024-08-18'
    )

    # Add and commit the new car to the session
    session.add(new_car)
    session.commit()

    # Query the car from the database
    car_from_db = session.query(Car).filter_by(title='Test Car').first()

    # Test if the car was successfully created and stored
    assert car_from_db is not None
    assert car_from_db.url == 'https://bama.ir/car-url'
    assert car_from_db.year == '2023'


def test_car_model_repr():
    # Create an instance of Car
    car = Car(title='Test Car', year='2023', location='Test City')
    assert repr(car) == "<Car(title='Test Car', year='2023', location='Test City')>"
