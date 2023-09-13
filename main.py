import os

from config import DATABASE_COLUMNS
from dotenv import load_dotenv
from notion_types import DatabaseClient
from csv_processor import CSVProcessor

if __name__ == "__main__":
    load_dotenv()
    database_client = DatabaseClient(
        os.environ["DATABASE_ID"],
        DATABASE_COLUMNS,
    )

    database_client.notion_clear_database()

    csv_processor = CSVProcessor("data/ratings.csv")

    # Reverse sorting for deterministic outputs
    for key in sorted(
        [str(dict_key) for dict_key in csv_processor.name_to_count.keys()], reverse=True
    ):
        row = {
            column.column_name: column.csv_processor_function(csv_processor, key)
            for column in DATABASE_COLUMNS
        }
        database_client.notion_add_row(row)
