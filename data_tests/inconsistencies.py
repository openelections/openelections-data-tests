class VoteBreakdownTotals:
    def __init__(self, headers: list[str]):
        self.__headers = headers
        self.__failures = {}
        self.__current_row = 0

        votes = "votes"
        if votes in self.__headers:
            self.__votes_index = self.__headers.index("votes")
        else:
            self.__votes_index = None

        components = {"absentee", "early_voting", "election_day", "mail", "provisional"}
        self.__component_indices = [i for i, x in enumerate(self.__headers) if x in components]

    @property
    def passed(self) -> bool:
        return len(self.__failures) == 0

    def get_failure_message(self, max_examples: int = 10) -> str:
        components = [self.__headers[i] for i in self.__component_indices]
        message = f"There are {len(self.__failures)} rows where the sum of {components} is greater than 'votes':\n\n" \
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

        if (len(row) == len(self.__headers)) and self.__votes_index and self.__component_indices:
            try:
                # We use float instead of int to allow for values like "3.0".
                votes = float(row[self.__votes_index])
            except ValueError:
                return

            component_sum = 0
            for component in (row[i] for i in self.__component_indices):
                try:
                    component_value = float(component)
                except ValueError:
                    component_value = 0
                component_sum += component_value

            if votes < component_sum:
                self.__failures[self.__current_row] = row
