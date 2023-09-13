import os

from config import DATABASE_COLUMNS
from dotenv import load_dotenv
from notion_types import DatabaseClient

if __name__ == "__main__":
    load_dotenv()
    database_client = DatabaseClient(
        os.environ["DATABASE_ID"],
        os.environ["PAGE_ID"],
        DATABASE_COLUMNS,
        test_mode=True,
    )

    database_client.notion_clear_database()
