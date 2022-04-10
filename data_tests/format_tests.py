import re
from abc import ABC, abstractmethod


class FormatTest(ABC):
    @property
    @abstractmethod
    def passed(self) -> bool:
        pass

    @abstractmethod
    def get_failure_message(self, max_examples: int) -> str:
        pass

    @abstractmethod
    def test(self, value):
        pass


# noinspection PyAbstractClass
class RowTest(FormatTest):
    def __init__(self):
        super().__init__()
        self.__current_row = 0

    @property
    def current_row(self) -> int:
        return self.__current_row

    def test(self, value):
        self.__current_row += 1
        self._test_row(value)

    @abstractmethod
    def _test_row(self, row: list[str]):
        pass


class ValueTest(RowTest):
    def __init__(self):
        super().__init__()
        self.__failures = {}

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def passed(self):
        return len(self.__failures) == 0

    def get_failure_message(self, max_examples=-1):
        message = f"There are {len(self.__failures)} rows that have entries with {self.description}:\n"
        count = 0
        for key, value in self.__failures.items():
            if (max_examples >= 0) and (count >= max_examples):
                message += f"\n\t[Truncated to {max_examples} examples]"
                return message
            else:
                message += f"\n\tRow {key}: {value}"
                count += 1

        return message

    @abstractmethod
    def is_bad_value(self, value) -> bool:
        pass

    def _test_row(self, row: list[str]):
        for entry in row:
            if self.is_bad_value(entry):
                self.__failures[self.current_row] = row
                break


class EmptyHeaders(FormatTest):
    def __init__(self):
        super().__init__()
        self.__headers = []
        self.__passed = True

    @property
    def passed(self):
        return self.__passed

    def get_failure_message(self, max_examples=0):
        return f"Header {self.__headers} has empty entries."

    def test(self, headers: list[str]):
        self.__headers = headers
        self.__passed = "" not in headers


class LowercaseHeaders(FormatTest):
    def __init__(self):
        super().__init__()
        self.__headers = []
        self.__passed = True

    @property
    def passed(self):
        return self.__passed

    def get_failure_message(self, max_examples=0):
        return f"Header {self.__headers} should only contain lowercase characters."

    def test(self, headers: list[str]):
        self.__headers = headers
        self.__passed = headers == [x.lower() for x in headers]


class MissingHeaders(FormatTest):
    def __init__(self, required_headers: set[str]):
        super().__init__()
        self.__headers = []
        self.__passed = True
        self.__required_headers = required_headers

    @property
    def passed(self):
        return self.__passed

    def get_failure_message(self, max_examples=0):
        return f"Header {self.__headers} is missing entries: {self.__required_headers.difference(self.__headers)}."

    def test(self, headers: list[str]):
        self.__headers = headers
        self.__passed = self.__required_headers.issubset(headers)


class UnknownHeaders(FormatTest):
    def __init__(self):
        super().__init__()
        self.__headers = []
        self.__passed = True

    @property
    def passed(self):
        return self.__passed

    def get_failure_message(self, max_examples=0):
        return f"Header {self.__headers} has unknown entries."

    def test(self, headers: list[str]):
        self.__headers = headers
        self.__passed = "unknown" not in [x.strip().lower() for x in headers]


class WhitespaceInHeaders(FormatTest):
    regex = re.compile(r"\s")

    def __init__(self):
        super().__init__()
        self.__headers = []
        self.__passed = True

    @property
    def passed(self):
        return self.__passed

    def get_failure_message(self, max_examples=0):
        return f"Header {self.__headers} contains whitespace characters."

    def test(self, headers: list[str]):
        self.__headers = headers
        self.__passed = not any(bool(WhitespaceInHeaders.regex.search(x)) for x in self.__headers)


class ConsecutiveSpaces(ValueTest):
    regex = re.compile(r"\s{2,}")

    @property
    def description(self):
        return "consecutive whitespace characters"

    def is_bad_value(self, value):
        return bool(ConsecutiveSpaces.regex.search(value))


class EmptyRows(RowTest):
    regex = re.compile(r"\S")

    def __init__(self):
        super().__init__()
        self.__empty_row_count = 0

    @property
    def passed(self):
        return self.__empty_row_count == 0

    def get_failure_message(self, max_examples=0):
        return f"Has {self.__empty_row_count} empty rows."

    def _test_row(self, row: list[str]):
        has_content = False
        for entry in row:
            has_content |= bool(EmptyRows.regex.search(entry))

        if not has_content:
            self.__empty_row_count += 1


class InconsistentNumberOfColumns(RowTest):
    def __init__(self, headers):
        super().__init__()
        self.__failures = {}
        self.__headers = headers

    @property
    def passed(self):
        return len(self.__failures) == 0

    def get_failure_message(self, max_examples=-1):
        message = f"Header has {len(self.__headers)} entries, but there are {len(self.__failures)} " \
                  f"rows with an inconsistent number of columns:\n\n" \
                  f"\tHeaders ({len(self.__headers)} entries): {self.__headers}:"

        count = 0
        for key, value in self.__failures.items():
            if (max_examples >= 0) and (count >= max_examples):
                message += f"\n\t[Truncated to {max_examples} examples]"
                return message
            else:
                message += f"\n\tRow {key} ({len(value)} entries): {value}"
                count += 1

        return message

    def _test_row(self, row: list[str]):
        if len(row) != len(self.__headers):
            self.__failures[self.current_row] = row


class NonIntegerVotes(RowTest):
    def __init__(self, headers: list[str]):
        super().__init__()
        self.__failures = {}
        self.__headers = headers

        columns_to_check = {"absentee", "early_voting", "election_day", "mail", "provisional", "votes"}
        lowercase_headers = [x.strip().lower() for x in headers]
        indices_to_check = []
        for index, header in enumerate(lowercase_headers):
            if header in columns_to_check:
                indices_to_check.append(index)
        self.__indices_to_check = indices_to_check

        if "candidate" in lowercase_headers:
            self.__candidate_index = lowercase_headers.index("candidate")
        else:
            self.__candidate_index = None

    @property
    def passed(self):
        return len(self.__failures) == 0

    def get_failure_message(self, max_examples=-1):
        message = f"There are {len(self.__failures)} rows with votes that aren't integers:\n\n" \
                  f"\tHeaders: {self.__headers}:"

        count = 0
        for key, value in self.__failures.items():
            if (max_examples >= 0) and (count >= max_examples):
                message += f"\n\t[Truncated to {max_examples} examples]"
                return message
            else:
                message += f"\n\tRow {key}: {value}"
                count += 1

        return message

    def _test_row(self, row: list[str]):
        if len(row) == len(self.__headers):
            for value in (row[i] for i in self.__indices_to_check):
                # There are some rare cases where the value represents a turnout percentage.  We will try and avoid
                # these rows.
                percentages = {"%", "pct", "percent"}
                if self.__candidate_index is not None \
                        and any(x in row[self.__candidate_index].lower() for x in percentages):
                    continue

                # If the value isn't numeric, skip the test.  This can be due to the row having an inconsistent
                # number of columns (hence the index of the "votes" column is invalid), or the value has been
                # redacted and is represented by a non-numeric character.
                try:
                    float_value = float(value)
                except ValueError:
                    continue

                # This allows for "3" and "3.0", but not "3.1".
                if not float(float_value).is_integer():
                    self.__failures[self.current_row] = row


class LeadingAndTrailingSpaces(ValueTest):
    @property
    def description(self):
        return "leading or trailing whitespace characters"

    def is_bad_value(self, value):
        return value != value.strip()


class NonAlphanumericEntries(ValueTest):
    regex = re.compile(r"\w")

    @property
    def description(self):
        return "only non-alphanumeric characters"

    def is_bad_value(self, value):
        return value != "" and not bool(NonAlphanumericEntries.regex.search(value))


class PrematureLineBreaks(ValueTest):
    @property
    def description(self):
        return "newline characters"

    def is_bad_value(self, value):
        return "\n" in value


class TabCharacters(ValueTest):
    @property
    def description(self):
        return "tab characters"

    def is_bad_value(self, value):
        return "\t" in value
