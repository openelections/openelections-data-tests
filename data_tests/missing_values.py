class MissingValue:
    def __init__(self, required_value: str, headers: list[str]):
        super().__init__()
        self.__current_row = 0
        self.__required_value = required_value
        self.__headers = headers
        self.__failures = {}

        if required_value in headers:
            self.__required_value_index = headers.index(required_value)
        else:
            self.__required_value_index = None

    @property
    def passed(self) -> bool:
        return len(self.__failures) == 0

    def get_failure_message(self, max_examples: int = -1) -> str:
        message = f"There are {len(self.__failures)} rows that are missing a {self.__required_value}:\n\n" \
                  f"\tHeaders: {self.__headers}:"

        count = 0
        for row_number, row in self.__failures.items():
            if (max_examples >= 0) and (count >= max_examples):
                message += f"\n\t[Truncated to {max_examples} examples]"
                return message
            else:
                message += f"\n\tRow {row_number}: {row}"
                count += 1

        return message

    def test(self, row: list[str]):
        self.__current_row += 1
        if self.__required_value_index is not None:
            if self.__required_value_index >= len(row):
                self.__failures[self.__current_row] = row
            else:
                value = row[self.__required_value_index]
                if not value or value.isspace():
                    self.__failures[self.__current_row] = row
