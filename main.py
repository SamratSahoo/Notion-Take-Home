import os

from config import DATABASE_COLUMNS
from dotenv import load_dotenv
from notion_types import DatabaseClient
from csv_processor import CSVProcessor

if __name__ == "__main__":
    load_dotenv()
    database_client = DatabaseClient(
        os.environ["DATABASE_ID"],
        os.environ["PAGE_ID"],
        DATABASE_COLUMNS,
        test_mode=True,
    )

    database_client.notion_clear_database()

    csv_processor = CSVProcessor("data/ratings.csv")

    for key in csv_processor.name_to_count:
        database_client.notion_add_row(
            {
                DATABASE_COLUMNS[0].column_name: key,
                DATABASE_COLUMNS[
                    1
                ].column_name: csv_processor.get_average_rating_by_book_name(key),
                DATABASE_COLUMNS[
                    2
                ].column_name: csv_processor.get_favorites_by_book_name(key),
            }
        )
