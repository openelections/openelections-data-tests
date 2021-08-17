import re
from hashlib import sha256


class DuplicateEntries:
    __non_whitespace_regex = re.compile(r"\S")

    def __init__(self):
        super().__init__()
        self.__current_row = 0
        self.__hash_to_row = {}
        self.__hash_to_row_numbers = {}

    @property
    def passed(self) -> bool:
        return len(self.__hash_to_row) == 0

    @staticmethod
    def __hash_row(row: list[str]) -> str:
        hashed_entries = [sha256(x.encode()).hexdigest() for x in row]
        return sha256("".join(hashed_entries).encode()).hexdigest()

    @staticmethod
    def __is_empty(row: list) -> bool:
        has_content = False
        for entry in row:
            has_content |= bool(DuplicateEntries.__non_whitespace_regex.search(entry))

        return not has_content

    def get_failure_message(self, max_examples: int = 10) -> str:
        num_duplicates = 0
        for _, rows in self.__hash_to_row_numbers.items():
            num_duplicates += len(rows) - 1

        message = f"{num_duplicates} duplicate rows detected:\n"
        count = 1
        for key, value in self.__hash_to_row.items():
            for row_number in self.__hash_to_row_numbers[key]:
                message += f"\n\tRow {row_number}: {value}"
                count += 1

                if count > max_examples:
                    message += f"\n\t[Truncated to {max_examples} examples]"
                    return message

        return message

    def test(self, row: list):
        if not DuplicateEntries.__is_empty(row):
            row_hash = DuplicateEntries.__hash_row(row)
            if row_hash in self.__hash_to_row_numbers:
                self.__hash_to_row_numbers[row_hash].append(self.__current_row)
                self.__hash_to_row[row_hash] = row
            else:
                self.__hash_to_row_numbers[row_hash] = [self.__current_row]

        self.__current_row += 1
