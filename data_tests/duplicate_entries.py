import re


class DuplicateEntries:
    _non_whitespace_regex = re.compile(r"\S")

    def __init__(self, headers: list[str]):
        super().__init__()
        self._current_row = 0
        self._hash_to_row_map = {}
        self._passed = True
        self._headers = headers

        indices_to_hash = []
        for i, x in enumerate(self._headers):
            lowered_header = x.lower()
            not_vote_column = "votes" not in lowered_header
            not_vote_column &= lowered_header not in {"absentee", "early_voting", "election_day", "mail", "provisional"}
            if not_vote_column:
                indices_to_hash.append(i)

        self._indices_to_hash = indices_to_hash

    @property
    def passed(self) -> bool:
        return self._passed

    def _hash_row(self, row: list[str]) -> int:
        if len(row) == len(self._headers):
            entries_to_hash = (row[i] for i in self._indices_to_hash)
        else:
            entries_to_hash = row

        hashed_entries = (hash(x) for x in entries_to_hash)
        return hash(tuple(hashed_entries))

    @staticmethod
    def _is_empty(row: list) -> bool:
        has_content = False
        for entry in row:
            has_content |= bool(DuplicateEntries._non_whitespace_regex.search(entry))

        return not has_content

    def get_failure_message(self, max_examples: int = -1) -> str:
        num_duplicates = 0
        for _, rows in self._hash_to_row_map.items():
            if len(rows) > 1:
                num_duplicates += len(rows) - 1

        message = f"{num_duplicates} duplicate entries detected:\n\n" \
                  f"\tHeaders: {self._headers}:"
        count = 0
        for row_hash, row_map in self._hash_to_row_map.items():
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
        self._current_row += 1
        if not DuplicateEntries._is_empty(row):
            row_hash = self._hash_row(row)
            if row_hash in self._hash_to_row_map:
                self._passed = False
                self._hash_to_row_map[row_hash][self._current_row] = row
            else:
                self._hash_to_row_map[row_hash] = {self._current_row: row}
