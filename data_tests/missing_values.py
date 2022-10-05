class MissingValue:
    def __init__(self, required_value: str, headers: list[str]):
        super().__init__()
        self._current_row = 0
        self._required_value = required_value
        self._headers = headers
        self._failures = {}

        if required_value in headers:
            self._required_value_index = headers.index(required_value)
        else:
            self._required_value_index = None

    @property
    def passed(self) -> bool:
        return len(self._failures) == 0

    def get_failure_message(self, max_examples: int = -1) -> str:
        message = f"There are {len(self._failures)} rows that are missing a {self._required_value}:\n\n" \
                  f"\tHeaders: {self._headers}:"

        count = 0
        for row_number, row in self._failures.items():
            if (max_examples >= 0) and (count >= max_examples):
                message += f"\n\t[Truncated to {max_examples} examples]"
                return message
            else:
                message += f"\n\tRow {row_number}: {row}"
                count += 1

        return message

    def test(self, row: list[str]):
        self._current_row += 1
        if self._required_value_index is not None:
            if self._required_value_index >= len(row):
                self._failures[self._current_row] = row
            else:
                value = row[self._required_value_index]
                if not value or value.isspace():
                    self._failures[self._current_row] = row
