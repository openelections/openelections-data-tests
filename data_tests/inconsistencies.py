class VoteBreakdownTotals:
    def __init__(self, headers: list[str]):
        self._headers = headers
        self._failures = {}
        self._current_row = 0

        votes = "votes"
        if votes in self._headers:
            self._votes_index = self._headers.index(votes)
        else:
            self._votes_index = None

        if "candidate" in self._headers:
            self._candidate_index = self._headers.index("candidate")
        else:
            self._candidate_index = None

        components = {"absentee", "early_voting", "election_day", "mail", "provisional"}
        self._component_indices = [i for i, x in enumerate(self._headers) if x in components]

        # If the column headers match some known schemas, we can check for exact equality.
        known_schemas = [
            {"county", "precinct", "office", "district", "party", "candidate", "votes", "early_voting", "election_day",
             "provisional", "mail"}
        ]
        self._check_equality = set(self._headers) in known_schemas

    @property
    def passed(self) -> bool:
        return len(self._failures) == 0

    def get_failure_message(self, max_examples: int = -1) -> str:
        components = [self._headers[i] for i in self._component_indices]
        if self._check_equality:
            relation = "not equal to"
        else:
            relation = "greater than"
        message = f"There are {len(self._failures)} rows where the sum of {components} is {relation} 'votes':\n\n" \
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

        if (len(row) == len(self._headers)) and self._votes_index is not None and self._component_indices:
            # There are cases where over votes and under votes are reported as a single aggregate.  As such, it's
            # possible for the votes to be negative.  We will try and avoid these rows.
            if self._candidate_index is not None:
                aggregates = {"over/under", "under/over"}
                if any(x in row[self._candidate_index].lower().replace(" ", "") for x in aggregates):
                    return

            try:
                # We use float instead of int to allow for values like "3.0".
                votes = float(row[self._votes_index])
            except ValueError:
                return

            component_sum = 0
            has_components = False
            for component in (row[i] for i in self._component_indices):
                try:
                    component_value = float(component)
                    has_components = True
                except ValueError:
                    component_value = 0
                component_sum += component_value

            if has_components:
                if self._check_equality:
                    if votes != component_sum:
                        self._failures[self._current_row] = row
                elif votes < component_sum:
                    self._failures[self._current_row] = row
