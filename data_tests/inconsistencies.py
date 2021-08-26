class VoteMethodTotals:
    def __init__(self, headers: list[str]):
        self.__headers = headers
        self.__failures = {}
        self.__current_row = 0

        votes = "votes"
        if votes in self.__headers:
            self.__votes_index = self.__headers.index("votes")
        else:
            self.__votes_index = None

        components = {"early_voting", "election_day", "mail", "provisional"}
        component_indices = None
        if set(headers).issuperset(components | {votes}):
            component_indices = [i for i, x in enumerate(self.__headers) if x in components]
        self.__component_indices = component_indices

    @property
    def passed(self) -> bool:
        return len(self.__failures) == 0

    def get_failure_message(self, max_examples: int = 10) -> str:
        message = f"There are {len(self.__failures)} rows with inconsistent vote values:\n\n" \
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

            # We will only compare the values if there is at least one component value.
            component_sum = 0
            has_component = False
            for component in (row[i] for i in self.__component_indices):
                try:
                    component_value = float(component)
                    has_component = True
                except ValueError:
                    component_value = 0

                component_sum += component_value

            if has_component and votes != component_sum:
                self.__failures[self.__current_row] = row
