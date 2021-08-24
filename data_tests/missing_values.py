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

    def get_failure_message(self, max_examples: int = 10) -> str:
        message = f"There are {len(self.__failures)} rows that are missing a {self.__required_value}:\n\n" \
                  f"\tHeaders: {self.__headers}:"

        count = 1
        for key, value in self.__failures.items():
            message += f"\n\tRow {key}: {value}"
            count += 1
            if count > max_examples:
                message += f"\n\t[Truncated to {max_examples} examples]"
                break

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
