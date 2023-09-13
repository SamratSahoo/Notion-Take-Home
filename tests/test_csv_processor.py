import pytest
from csv_processor import CSVProcessor


TEST_DATA = "../data/sample.csv"


@pytest.fixture(autouse=True)
def pytest_configure():
    """Creates a global CSV Processor to use across all tests"""
    pytest.csv_processor = CSVProcessor(TEST_DATA)


def test_csv_processor_favorites():
    """Tests whether we get the correct number of favorites"""
    favorites = pytest.csv_processor.get_favorites_by_book_name("Book 1")
    assert favorites == 4


def test_csv_processor_average_rating():
    """Tests whether we get the correct average rating"""
    average_rating = pytest.csv_processor.get_average_rating_by_book_name("Book 1")
    assert average_rating == 4.8


def test_replaced_average_rating():
    """Tests whether we get the correct average rating after a replacement further down the CSV file"""
    average_rating = pytest.csv_processor.get_average_rating_by_book_name("Book 2")
    assert average_rating == 4
