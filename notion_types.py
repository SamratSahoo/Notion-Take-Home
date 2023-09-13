import enum
from notion_client import Client
from dotenv import load_dotenv
import os


class NotionType(str, enum.Enum):
    TEXT = "rich_text"
    NUMBER = "number"
    TITLE = "title"


class NotionResponseObject(str, enum.Enum):
    ERROR = "error"
    DATABASE = "database"


class DatabaseColumn:
    def __init__(
        self, column_name: str, column_type: str, sanatizers=[], is_primary=False
    ) -> None:
        self.column_name = column_name
        self.column_type = column_type
        self.sanatizers = sanatizers
        self.is_primary = is_primary


class Sanatizers:
    @staticmethod
    def clear_white_space(input_value: str) -> str:
        return input_value.strip()

    @staticmethod
    def clear_capitalization(input_value: str) -> str:
        return input_value.lower()


class DatabaseActions(enum.Enum):
    ADD_COLUMN = "add column"
    GET_ALL_COLUMNS = "get all columns"
    INSERT_ROW = "insert row"
    REMOVE_COLUMN = "remove column"


class DatabaseClient:
    """A database client to easily interact with a specified notion database"""

    def __init__(
        self,
        database_id: str,
        page_id: str,
        columns: "list[DatabaseColumn]",
        test_mode=False,
    ) -> None:
        """Initializes a database client based on the database id and columns.
        Will add columns to the notion database if they do not exist already.
        Will remove columns that are not intended to be in the database.

        Args:
            database_id (str): Id of database to interact with
            columns (list[DatabaseColumn]): List of columns we want to
            test_mode (bool): Whether or not we want to use the database in testing mode
        """
        load_dotenv()
        self.client = Client(auth=os.environ["NOTION_TOKEN"])
        self.database_id = database_id
        self.page_id = page_id
        self.columns = columns
        self.notion_column_keys = self.notion_get_all_column_keys()
        self.test_mode = test_mode

        if not test_mode:
            intended_column_keys = set([column.column_name for column in self.columns])
            for key in self.notion_column_keys:
                if key not in intended_column_keys:
                    self.notion_create_database_column(key)

            for column in self.columns:
                if column.column_name not in self.notion_column_keys:
                    self.notion_create_database_column(column)

    def notion_get_all_column_keys(self) -> "set[str]":
        """
        Gets all column keys that have been added into the notion database.

        Raises:
            Exception: Failure to retrieve column keys for a specified database based on the database id

        Returns:
            set[str]: Set of strings indicating all column database keys
        """
        response = self.client.databases.retrieve(self.database_id)
        properties = set()

        if response["object"] != NotionResponseObject.DATABASE:
            raise Exception(
                f"Failed to retrieve column keys for database: {self.database_id}"
            )

        properties_object = response["properties"]
        for key in properties_object:
            properties.add(key)

        return properties

    def notion_create_database_column(self, column: DatabaseColumn) -> None:
        self.client.databases.update(
            self.database_id,
            properties=self.__construct_action_payload(
                DatabaseActions.ADD_COLUMN, column
            ),
        )

    def notion_add_row(self, data: type(dict)) -> None:
        self.client.pages.create(
            properties=self.__construct_action_payload(
                DatabaseActions.INSERT_ROW, data
            ),
            parent={"type": "database_id", "database_id": self.database_id},
        )

    def notion_remove_database_column(self, column_key: str) -> None:
        self.client.databases.update(
            self.database_id,
            properties=self.__construct_action_payload(
                DatabaseActions.REMOVE_COLUMN, column_key
            ),
        )

    def notion_clear_database(self) -> None:
        cursor = None
        page_size = 100
        all_pages = []
        while True:
            pages = self.client.databases.query(
                self.database_id, start_cursor=cursor, page_size=page_size
            )

            all_pages.extend(pages["results"])

            if "has_more" not in pages or not pages["has_more"]:
                break

            cursor = pages["next_cursor"]

        for page in all_pages:
            self.client.pages.update(page["id"], archived=True)

    def __construct_action_payload(self, action: DatabaseActions, payload):
        if action == DatabaseActions.ADD_COLUMN:
            assert isinstance(payload, DatabaseColumn)

            if payload.is_primary:
                return {"title": {"name": payload.column_name}}

            return {
                payload.column_name: {
                    "id": payload.column_name.lower(),
                    "name": payload.column_name,
                    payload.column_type: {},
                }
            }

        if action == DatabaseActions.REMOVE_COLUMN:
            assert isinstance(payload, str)
            return {payload: None}

        if action == DatabaseActions.INSERT_ROW:
            input_payload = {}
            for column in self.columns:
                input_value = payload[column.column_name]
                for sanitizer in column.sanatizers:
                    input_value = sanitizer(input_value)

                if column.column_type == NotionType.NUMBER:
                    input_payload[column.column_name] = {
                        column.column_type.value: input_value
                    }
                elif (
                    column.column_type == NotionType.TEXT
                    or column.column_type == NotionType.TITLE
                ):
                    input_payload[column.column_name] = {
                        column.column_type.value: [{"text": {"content": input_value}}]
                    }

            return input_payload
