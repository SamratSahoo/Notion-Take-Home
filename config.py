from notion_types import DatabaseColumn, NotionType, Sanatizers


DATABASE_COLUMNS = [
    DatabaseColumn("Book Title", NotionType.TEXT, [Sanatizers.clear_white_space, Sanatizers.clear_capitalization]),
    DatabaseColumn("Rating", NotionType.NUMBER),
    DatabaseColumn("Number of Favorites", NotionType.NUMBER)
]