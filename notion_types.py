import enum
from notion_client import Client
from dotenv import load_dotenv
import os


class NotionType(enum.Enum):
    TEXT = "text"
    NUMBER = "number"


class NotionResponseObject(enum.Enum):
    ERROR = "error"
    DATABASE = "database"


class DatabaseColumn:
    def __init__(self, column_name: str, column_type: str, sanatizers=[]) -> None:
        self.column_name = column_name
        self.column_type = column_type
        self.sanatizers = sanatizers


class Sanatizers:
    def clear_white_space(self, input_value: str) -> str:
        return input_value.strip()

    def clear_capitalization(self, input_value: str) -> str:
        return input_value.lower()


class DatabaseActions(enum.Enum):
    ADD_COLUMN = "add column"
    GET_ALL_COLUMNS = "get all columns"
    INSERT_ROW = "insert row"


"""

"""


class DatabaseClient:
    """A database client to easily interact with a specified notion database"""

    def __init__(self, database_id: str, columns: "list[DatabaseColumn]") -> None:
        """Initializes a database client based on the database id and columns.
        Will add columns to the notion database if they do not exist already.
        Will remove columns that are not intended to be in the database.

        Args:
            database_id (str): Id of database to interact with
            columns (list[DatabaseColumn]): List of columns we want to
        """
        load_dotenv()
        self.client = Client(auth=os.environ["NOTION_TOKEN"])
        self.database_id = database_id
        self.columns = columns
        self.notion_column_keys = self.__notion_get_all_column_keys()

        intended_column_keys = set([column.column_name for column in self.columns])
        for key in self.notion_column_keys:
            if key not in intended_column_keys:
                self.__notion_remove_database_column(key)

        for column in self.columns:
            if column.column_name not in self.notion_column_keys:
                self.__notion_create_database_column(column)

    def __notion_get_all_column_keys(self) -> "set[str]":
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

    def __notion_create_database_column(self, column: DatabaseColumn) -> None:
        self.client.databases.update(
            self.database_id,
            self.__construct_action_payload(DatabaseActions.ADD_COLUMN, column),
        )

    def __notion_add_row() -> None:
        pass

    def __notion_remove_database_column(self, column_key: str) -> None:
        pass

    def __notion_clear_database() -> None:
        pass

    def import_csv(self):
        pass

    def __construct_action_payload(self, action: DatabaseActions, payload):
        if action == DatabaseActions.ADD_COLUMN:
            assert isinstance(payload, DatabaseColumn)
            return {
                "properties": {
                    payload.column_name: {
                        "id": payload.column_name.lower(),
                        "type": payload.column_type,
                        "name": payload.column_name,
                    }
                }
            }

        if action == DatabaseActions.INSERT_ROW:
            pass
