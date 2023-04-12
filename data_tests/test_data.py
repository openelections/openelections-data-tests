import csv
import glob
import logging
import os
import pathlib
import unittest
from typing import Iterator

from data_tests import format_tests
from data_tests.duplicate_entries import DuplicateEntries
from data_tests.inconsistencies import VoteBreakdownTotals
from data_tests.missing_values import MissingValue


class TestResult(unittest.TextTestResult):
    # noinspection PyTypeChecker
    def printErrorList(self, flavour, errors):
        group_map = {}
        ungrouped_errors = []
        for test, error in errors:
            if "group" in test.params:
                group = test.params["group"]
                if group in group_map:
                    group_map[group].append((test, error))
                else:
                    group_map[group] = [(test, error)]
            else:
                ungrouped_errors.append((test, error))

        for group in sorted(group_map.keys()):
            self.stream.write(f"::group::{group}\n")
            super().printErrorList(flavour, group_map[group])
            self.stream.write("::endgroup::\n")

        super().printErrorList(flavour, ungrouped_errors)


class TestCase(unittest.TestCase):
    files = list()
    log_file = None
    max_examples = -1
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    truncate_log_file = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if TestCase.log_file is None:
            self._logger = None
        else:
            self._logger = TestCase._get_logger(type(self).__name__, TestCase.log_file)

    def _assertTrue(self, result: bool, description: str, console_message: str, log_message: str):
        if not result:
            self._log_failure(description, log_message)
        self.assertTrue(result, console_message)

    def _log_failure(self, description: str, message: str):
        if self._logger is not None:
            self._logger.debug("======================================================================")
            self._logger.debug(f"FAIL: {description}")
            self._logger.debug("----------------------------------------------------------------------")
            self._logger.debug(f"{message}\n")

    def get_csv_files(self) -> Iterator[str]:
        if TestCase.files:
            file_list = [os.path.join(TestCase.root_path, x) for x in TestCase.files]
        else:
            file_list = glob.glob(os.path.join(TestCase.root_path, "[0-9]" * 4, "**", "*"), recursive=True)

        for file in file_list:
            if file.lower().endswith(".csv"):
                short_path = os.path.relpath(file, start=TestCase.root_path)
                year = pathlib.Path(short_path).parts[0]
                yield file, short_path, year

    @staticmethod
    def _get_logger(name: str, log_file: str) -> logging.Logger:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        return logger


class DuplicateEntriesTest(TestCase):
    def test_duplicate_entries(self):
        log_file_max_examples = TestCase.max_examples if TestCase.truncate_log_file else -1
        for csv_file, short_path, year in self.get_csv_files():
            with self.subTest(msg=f"{short_path}", group=year):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    data_test = DuplicateEntries(headers)
                    data_test.test(headers)
                    for row in reader:
                        data_test.test(row)

                console_message = data_test.get_failure_message(max_examples=TestCase.max_examples)
                log_message = data_test.get_failure_message(max_examples=log_file_max_examples)
                self._assertTrue(data_test.passed, f"{self} [{short_path}]", console_message, log_message)


class FileFormatTests(TestCase):
    def test_format(self):
        log_file_max_examples = TestCase.max_examples if TestCase.truncate_log_file else -1
        for csv_file, short_path, year in self.get_csv_files():
            tests = set()

            header_tests = {
                format_tests.EmptyHeaders(),
                format_tests.LowercaseHeaders(),
                format_tests.UnknownHeaders(),
                format_tests.WhitespaceInHeaders(),
            }
            tests.update(header_tests)

            tests.add(format_tests.ConsecutiveSpaces())
            tests.add(format_tests.EmptyRows())
            tests.add(format_tests.LeadingAndTrailingSpaces())
            tests.add(format_tests.PrematureLineBreaks())
            tests.add(format_tests.TabCharacters())

            with self.subTest(msg=f"{short_path}", group=year):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    tests.add(format_tests.InconsistentNumberOfColumns(headers))
                    tests.add(format_tests.NegativeVotes(headers))
                    tests.add(format_tests.NonIntegerVotes(headers))

                    for test in tests:
                        test.test(headers)

                    row_tests = tests - header_tests
                    for row in reader:
                        for test in row_tests:
                            test.test(row)

                passed = True
                console_message = ""
                log_message = ""
                is_first_message = True
                for test in sorted(tests, key=lambda x: type(x).__name__):
                    if not test.passed:
                        passed = False
                        console_message += f"\n\n* {test.get_failure_message(max_examples=TestCase.max_examples)}"
                        if not is_first_message:
                            log_message += "\n\n"
                        log_message += f"* {test.get_failure_message(max_examples=log_file_max_examples)}"
                        is_first_message = False

                self._assertTrue(passed, f"{self} [{short_path}]", console_message, log_message)


class MissingValuesTest(TestCase):
    def test_missing_values(self):
        log_file_max_examples = TestCase.max_examples if TestCase.truncate_log_file else -1
        for csv_file, short_path, year in self.get_csv_files():
            with self.subTest(msg=f"{short_path}", group=year):
                tests = []
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    tests.append(MissingValue("county", headers))
                    tests.append(MissingValue("precinct", headers))
                    tests.append(MissingValue("office", headers))

                    for test in tests:
                        test.test(headers)

                    for row in reader:
                        for test in tests:
                            test.test(row)

                passed = True
                console_message = ""
                log_message = ""
                is_first_message = True
                for test in tests:
                    if not test.passed:
                        passed = False
                        console_message += f"\n\n* {test.get_failure_message(max_examples=TestCase.max_examples)}"
                        if not is_first_message:
                            log_message += "\n\n"
                        log_message += f"* {test.get_failure_message(max_examples=log_file_max_examples)}"
                        is_first_message = False

                self._assertTrue(passed, f"{self} [{short_path}]", console_message, log_message)


class VoteBreakdownTotalsTest(TestCase):
    def test_vote_method_totals(self):
        log_file_max_examples = TestCase.max_examples if TestCase.truncate_log_file else -1
        for csv_file, short_path, year in self.get_csv_files():
            with self.subTest(msg=f"{short_path}", group=year):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    data_test = VoteBreakdownTotals(headers)
                    data_test.test(headers)
                    for row in reader:
                        data_test.test(row)

                console_message = data_test.get_failure_message(max_examples=TestCase.max_examples)
                log_message = data_test.get_failure_message(max_examples=log_file_max_examples)
                self._assertTrue(data_test.passed, f"{self} [{short_path}]", console_message, log_message)
