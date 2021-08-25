import re
from hashlib import sha256


class DuplicateEntries:
    __non_whitespace_regex = re.compile(r"\S")

    def __init__(self, headers: list[str]):
        super().__init__()
        self.__current_row = 0
        self.__hash_to_rows = {}
        self.__passed = True
        self.__headers = headers

        indices_to_hash = []
        for i, x in enumerate(self.__headers):
            lowered_header = x.lower()
            not_vote_column = "votes" not in lowered_header
            not_vote_column &= lowered_header not in ["early_voting", "election_day", "mail", "provisional"]
            if not_vote_column:
                indices_to_hash.append(i)

        self.__indices_to_hash = indices_to_hash

    @property
    def passed(self) -> bool:
        return self.__passed

    def __hash_row(self, row: list[str]) -> str:
        if len(row) == len(self.__headers):
            entries_to_hash = [row[i] for i in self.__indices_to_hash]
        else:
            entries_to_hash = row

        hashed_entries = [sha256(x.encode()).hexdigest() for x in entries_to_hash]
        return sha256("".join(hashed_entries).encode()).hexdigest()

    @staticmethod
    def __is_empty(row: list) -> bool:
        has_content = False
        for entry in row:
            has_content |= bool(DuplicateEntries.__non_whitespace_regex.search(entry))

        return not has_content

    def get_failure_message(self, max_examples: int = -1) -> str:
        num_duplicates = 0
        for _, rows in self.__hash_to_rows.items():
            if len(rows) > 1:
                num_duplicates += len(rows) - 1

        message = f"{num_duplicates} duplicate entries detected:\n\n" \
          f"\tHeaders: {self.__headers}:"
        count = 0
        for row_hash, row_map in self.__hash_to_rows.items():
            if len(row_map) > 1:
                for row_number, row in row_map.items():
                    if (max_examples >= 0) and (count >= max_examples):
                        message += f"\n\t[Truncated to {max_examples} examples]"
                        return message
                    else:
                        message += f"\n\tRow {row_number}: {row}"
                        count += 1

        return message

    def test(self, row: list):
        self.__current_row += 1
        if not DuplicateEntries.__is_empty(row):
            row_hash = self.__hash_row(row)
            if row_hash in self.__hash_to_rows:
                self.__passed = False
                self.__hash_to_rows[row_hash][self.__current_row] = row
            else:
                self.__hash_to_rows[row_hash] = {self.__current_row: row}
