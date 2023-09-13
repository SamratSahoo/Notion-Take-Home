from notion_types import DatabaseColumn, NotionType, Sanatizers


DATABASE_COLUMNS = [
    DatabaseColumn(
        "Book Title",
        NotionType.TITLE,
        sanatizers=[Sanatizers.clear_white_space, Sanatizers.clear_capitalization],
        is_primary=True,
    ),
    DatabaseColumn("Rating", NotionType.NUMBER),
    DatabaseColumn("Number of Favorites", NotionType.NUMBER),
]
