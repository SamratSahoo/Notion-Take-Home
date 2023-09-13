from collections import defaultdict
from notion_types import Sanatizers


class CSVProcessor:
    def __init__(self, csv_path) -> None:
        with open(csv_path, "r") as file:
            self.csv_contents = file.read()

        # Reverse so that we only keep track of the most recent ratings
        self.rows = self.csv_contents.split("\n")[::-1]
        self.name_to_average_rating = defaultdict(float)
        self.name_to_count = defaultdict(int)
        self.name_to_favorites = defaultdict(int)
        self.name_to_book_to_has_read = defaultdict(lambda: defaultdict(bool))

        self.__populate_info()

    def __populate_info(self):
        for row in self.rows:
            if not row:
                continue

            book_name, user, rating = row.split(",")
            book_name = Sanatizers.clear_capitalization(book_name)
            book_name = Sanatizers.clear_white_space(book_name)
            user = Sanatizers.clear_capitalization(user)
            user = Sanatizers.clear_white_space(user)

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

    def get_favorites_by_book_name(self, book_name):
        book_name = Sanatizers.clear_capitalization(book_name)
        book_name = Sanatizers.clear_white_space(book_name)

        return self.name_to_favorites[book_name]

    def get_average_rating_by_book_name(self, book_name):
        book_name = Sanatizers.clear_capitalization(book_name)
        book_name = Sanatizers.clear_white_space(book_name)

        return self.name_to_average_rating[book_name]
