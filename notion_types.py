import enum
from notion_client import Client
from dotenv import load_dotenv
import os


class NotionType(str, enum.Enum):
    """
    An enum to help us keep track of native notion types and easily modify our database schema
    """

    TEXT = "rich_text"
    NUMBER = "number"
    TITLE = "title"


class NotionResponseObject(str, enum.Enum):
    """
    An enum to help us keep track of native notion response objects and handle results from the response
    """

    ERROR = "error"


class DatabaseColumn:
    def __init__(
        self,
        column_name: str,
        column_type: str,
        csv_processor_function=None,
        sanitizers=[],
        is_primary=False,
    ) -> None:
        """Initializes a new database column that can be used in the notion database

        Args:
            column_name (str): The name of the column
            column_type (str): The type of the column (based on NotionType)
            csv_processor_function ((str) => None, optional): A value processor function that gives us a value for a given book. Defaults to None.
            sanitizers (list, optional): Input sanitation functions. Defaults to [].
            is_primary (bool, optional): Primary key of the database schema. Defaults to False.
        """
        self.column_name = column_name
        self.column_type = column_type
        self.sanitizers = sanitizers
        self.is_primary = is_primary
        self.csv_processor_function = csv_processor_function


class Sanitizers:
    @staticmethod
    def clear_white_space(input_value: str) -> str:
        """Sanitizer to clear whitespace around a string

        Args:
            input_value (str): Input value to sanitize

        Returns:
            str: Output value with all whitespace stripped
        """
        return input_value.strip()

    @staticmethod
    def clear_capitalization(input_value: str) -> str:
        """Sanitizer to clear capitalization within a string

        Args:
            input_value (str): Input value to sanitize

        Returns:
            str: Output value with all capitalization removed
        """

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

        if response["object"] == NotionResponseObject.ERROR:
            raise Exception(
                f"Failed to retrieve column keys for database: {self.database_id}"
            )

        properties_object = response["properties"]
        for key in properties_object:
            properties.add(key)

        return properties

    def notion_create_database_column(self, column: DatabaseColumn) -> None:
        """Creates a database column based on a database column object

        Args:
            column (DatabaseColumn): The database column information we want to create the column for

        Raises:
            Exception: Failure to create a database column
        """
        response = self.client.databases.update(
            self.database_id,
            properties=self.__construct_action_payload(
                DatabaseActions.ADD_COLUMN, column
            ),
        )

        if response["object"] == NotionResponseObject.ERROR:
            raise Exception(
                f"Failed to create database column for database: {self.database_id}"
            )

    def notion_add_row(self, data: type(dict)) -> None:
        """Creates a database row based on an object

        Args:
            data (type): Object with all the row information (key = column, value = column value for that row)

        Raises:
            Exception: Failure to create a database row
        """
        response = self.client.pages.create(
            properties=self.__construct_action_payload(
                DatabaseActions.INSERT_ROW, data
            ),
            parent={"type": "database_id", "database_id": self.database_id},
        )

        if response["object"] == NotionResponseObject.ERROR:
            raise Exception(
                f"Failed to create database row for database: {self.database_id}"
            )

    def notion_remove_database_column(self, column_key: str) -> None:
        """Removes a database column

        Args:
            column_key (str): Key of the column that needs to be removed

        Raises:
            Exception: Failure to remove a database column
        """
        response = self.client.databases.update(
            self.database_id,
            properties=self.__construct_action_payload(
                DatabaseActions.REMOVE_COLUMN, column_key
            ),
        )

        if response["object"] == NotionResponseObject.ERROR:
            raise Exception(
                f"Failed to remove database column for database: {self.database_id}"
            )

    def notion_clear_database(self) -> None:
        """Clears all rows in the notion database

        Raises:
            Exception: Failure to clear the database
        """
        all_pages = self.notion_get_rows()
        for page in all_pages:
            response = self.client.pages.update(page["id"], archived=True)

            if response["object"] == NotionResponseObject.ERROR:
                raise Exception(
                    f"Failed to archive page for database: {self.database_id}"
                )

    def notion_get_rows(self):
        """Gets all rows in the notion database

        Raises:
            Exception: Failure to get all rows in the database

        Returns:
            Page[]: Array of notion page objects with each object representing a row in the database
        """
        cursor = None
        page_size = 100
        all_pages = []
        while True:
            pages = self.client.databases.query(
                self.database_id, start_cursor=cursor, page_size=page_size
            )

            if pages["object"] == NotionResponseObject.ERROR:
                raise Exception(f"Failed to get rows for database: {self.database_id}")

            all_pages.extend(pages["results"])

            if "has_more" not in pages or not pages["has_more"]:
                break

            cursor = pages["next_cursor"]

        return all_pages

    def __construct_action_payload(self, action: DatabaseActions, payload):
        """Constructs the notion API payload based on the database action

        Args:
            action (DatabaseActions): The action we want to take with Notion API
            payload (_type_): Additional payload information that we use to construct our payload

        Returns:
            Object: An object representing the request payload
        """
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
                # Apply Sanitation
                for sanitizer in column.sanitizers:
                    input_value = sanitizer(input_value)

                # Handle numbers and text/title differently
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
