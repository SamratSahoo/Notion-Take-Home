import pytest
from notion_types import DatabaseClient
from config import DATABASE_COLUMNS
from dotenv import load_dotenv
import os


@pytest.fixture(autouse=True)
def pytest_configure():
    """Creates a global Notion database client to use across tests"""
    load_dotenv()
    pytest.database_client = DatabaseClient(
        os.environ["DATABASE_ID"],
        DATABASE_COLUMNS,
        test_mode=True,
    )
    pytest.database_client.notion_clear_database()


def test_database_add_columns():
    """Tests whether we can add the columns in correctly"""
    assert isinstance(pytest.database_client, DatabaseClient)
    for column in DATABASE_COLUMNS:
        pytest.database_client.notion_create_database_column(column)
        assert column.column_name in pytest.database_client.notion_get_all_column_keys()


def test_database_remove_column():
    """Tests whether we can remove the columns correctly"""
    assert isinstance(pytest.database_client, DatabaseClient)
    for column in DATABASE_COLUMNS:
        if not column.is_primary:
            pytest.database_client.notion_remove_database_column(column.column_name)
            assert (
                column.column_name
                not in pytest.database_client.notion_get_all_column_keys()
            )
        else:
            assert (
                column.column_name
                in pytest.database_client.notion_get_all_column_keys()
            )

    for column in DATABASE_COLUMNS:
        pytest.database_client.notion_create_database_column(column)


def test_database_add_row():
    """Tests whether we can add a row of information in correctly"""
    assert isinstance(pytest.database_client, DatabaseClient)
    data = {
        DATABASE_COLUMNS[0].column_name: "Hello World",
        DATABASE_COLUMNS[1].column_name: 1,
        DATABASE_COLUMNS[2].column_name: 2,
    }

    pytest.database_client.notion_add_row(data)
    assert len(pytest.database_client.notion_get_rows()) == 1


def test_database_clear_rows():
    """Tests whether we can clear all rows correctly"""
    assert isinstance(pytest.database_client, DatabaseClient)
    data = {
        DATABASE_COLUMNS[0].column_name: "Hello World",
        DATABASE_COLUMNS[1].column_name: 1,
        DATABASE_COLUMNS[2].column_name: 2,
    }

    pytest.database_client.notion_add_row(data)
    assert len(pytest.database_client.notion_get_rows()) == 1
    pytest.database_client.notion_clear_database()
    assert len(pytest.database_client.notion_get_rows()) == 0
