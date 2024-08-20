import pytest
from unittest.mock import patch, MagicMock
from database.db_manager import DatabaseManager
from models.car import Car


@pytest.fixture
def db_manager():
    return DatabaseManager('sqlite:///:memory:')  # Using an in-memory database for testing


def test_add_instance_success(db_manager):
    mock_session = MagicMock()

    # Mock the methods to be used in the test
    with patch.object(db_manager, 'get_session', return_value=mock_session):
        car_data = {
            'url': 'https://bama.ir/car-url',
            'title': 'Car Title',
            'time': '2024-08-19',
            'year': '2023',
            'mileage': '5000',
            'location': 'City',
            'description': 'A good car',
            'image': 'car.jpg',
            'modified_date': '2024-08-18'
        }

        db_manager.add_instance(Car, car_data)

        mock_session.add.assert_called_once()

        mock_session.commit.assert_called_once()


def test_add_instance_failure(db_manager):
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Commit failed")

    with patch.object(db_manager, 'get_session', return_value=mock_session):
        car_data = {
            'url': 'https://bama.ir/car-url',
            'title': 'Car Title',
            'time': '2024-08-19',
            'year': '2023',
            'mileage': '5000',
            'location': 'City',
            'description': 'A good car',
            'image': 'car.jpg',
            'modified_date': '2024-08-18'
        }

        db_manager.add_instance(Car, car_data)

        mock_session.add.assert_called_once()
        # Check that session.rollback() was called after commit failed
        mock_session.rollback.assert_called_once()
        # Check that session.commit() was called once and failed
        mock_session.commit.assert_called_once()


def test_close_session(db_manager):
    with patch.object(db_manager.Session, 'remove') as mock_remove:
        db_manager.close_session()
        mock_remove.assert_called_once()
