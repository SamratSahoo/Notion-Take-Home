from collections import defaultdict
from notion_types import Sanitizers


class CSVProcessor:
    # Edge Case Consideration: This has not been included because the assignment gave us confidence in a properly formatted
    # CSV, however, having stronger santiation and parsing mechanisms would be beneficial for edge cases where users input
    # malformed data
    def __init__(self, csv_path: str) -> None:
        """Creates an instance of a CSV Processor and processes the contents from a file

        Args:
            csv_path (str): The path of the CSV file we want to process
        """
        with open(csv_path, "r") as file:
            self.csv_contents = file.read()

        # Reverse rows so that we only keep track of the most recent ratings
        self.rows = self.csv_contents.split("\n")[::-1]
        self.name_to_average_rating = defaultdict(float)
        self.name_to_count = defaultdict(int)
        self.name_to_favorites = defaultdict(int)
        self.name_to_book_to_has_read = defaultdict(lambda: defaultdict(bool))

        self.__populate_info()

    def __populate_info(self):
        """Iterates through the rows, sanitizes the inputs, and logs the different metrics we want to calculate"""
        for row in self.rows:
            if not row:
                continue

            book_name, user, rating = row.split(",")
            book_name = Sanitizers.clear_capitalization(book_name)
            book_name = Sanitizers.clear_white_space(book_name)
            user = Sanitizers.clear_capitalization(user)
            user = Sanitizers.clear_white_space(user)

            if self.name_to_book_to_has_read[book_name][user]:
                continue

            self.name_to_book_to_has_read[book_name][user] = True

            count = self.name_to_count[book_name]
            current_avg = self.name_to_average_rating[book_name]

            # Calculate Average
            self.name_to_average_rating[book_name] = (
                current_avg * count + float(rating)
            ) / (count + 1)
            self.name_to_count[book_name] += 1

            if float(rating) == 5:
                self.name_to_favorites[book_name] += 1

    def get_favorites_by_book_name(self, book_name: str) -> int:
        """Sanitizes the book name and returns the number of people that have favorited the book by name

        Args:
            book_name (str): Name of the book we want to get the favorite count for

        Returns:
            int: Number of people who have that book as a favorite
        """
        book_name = Sanitizers.clear_capitalization(book_name)
        book_name = Sanitizers.clear_white_space(book_name)

        return self.name_to_favorites[book_name]

    def get_average_rating_by_book_name(self, book_name: str) -> float:
        """Sanitizes the book name and returns the average rating of a book by name

        Args:
            book_name (str): Name of the book we want to get the average rating for

        Raises:
            Exception: Failure to find average rating of book

        Returns:
            float: The average rating for that book
        """
        book_name = Sanitizers.clear_capitalization(book_name)
        book_name = Sanitizers.clear_white_space(book_name)

        if book_name not in self.name_to_average_rating:
            raise Exception(f"Book, {book_name}'s average rating cannot be found")

        return self.name_to_average_rating[book_name]

    def get_book_name(self, book_name: str) -> str:
        """Get the sanitized book name

        Args:
            book_name (str): Name of the book

        Returns:
            str: The name of the book
        """
        book_name = Sanitizers.clear_capitalization(book_name)
        book_name = Sanitizers.clear_white_space(book_name)

        return book_name
