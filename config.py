from notion_types import DatabaseColumn, NotionType, Sanitizers
from csv_processor import CSVProcessor

DATABASE_COLUMNS = [
    DatabaseColumn(
        "Book Title",
        NotionType.TITLE,
        csv_processor_function=CSVProcessor.get_book_name,
        sanitizers=[Sanitizers.clear_white_space, Sanitizers.clear_capitalization],
        is_primary=True,
    ),
    DatabaseColumn(
        "Rating",
        NotionType.NUMBER,
        csv_processor_function=CSVProcessor.get_average_rating_by_book_name,
    ),
    DatabaseColumn(
        "Number of Favorites",
        NotionType.NUMBER,
        csv_processor_function=CSVProcessor.get_favorites_by_book_name,
    ),
]
