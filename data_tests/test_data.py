import csv
import glob
import logging
import os
import unittest
from typing import Iterator

from data_tests.duplicate_entries import DuplicateEntries
from data_tests.inconsistencies import VoteBreakdownTotals


def get_csv_files(root_path: str) -> Iterator[str]:
    for file in glob.glob(os.path.join(root_path, "[0-9]" * 4, "**", "*"), recursive=True):
        if file.lower().endswith(".csv"):
            yield file


class TestCase(unittest.TestCase):
    log_file = None
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if TestCase.log_file is None:
            self.__logger = None
        else:
            self.__logger = TestCase.__get_logger(type(self).__name__, TestCase.log_file)

    def _assertTrue(self, result: bool, description: str, short_message: str, full_message: str):
        if not result:
            self._log_failure(description, full_message)
        self.assertTrue(result, short_message)

    def _log_failure(self, description: str, message: str):
        if self.__logger is not None:
            self.__logger.debug("======================================================================")
            self.__logger.debug(f"FAIL: {description}")
            self.__logger.debug("----------------------------------------------------------------------")
            self.__logger.debug(f"{message}\n")

    @staticmethod
    def __get_logger(name: str, log_file: str) -> logging.Logger:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        return logger


class DuplicateEntriesTest(TestCase):
    def test_duplicate_entries(self):
        for csv_file in get_csv_files(TestCase.root_path):
            short_path = os.path.relpath(csv_file, start=TestCase.root_path)

            with self.subTest(msg=f"{short_path}"):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    data_test = DuplicateEntries(headers)
                    data_test.test(headers)
                    for row in reader:
                        data_test.test(row)

                short_message = data_test.get_failure_message(max_examples=10)
                full_message = data_test.get_failure_message()
                self._assertTrue(data_test.passed, f"{self} [{short_path}]", short_message, full_message)


class VoteBreakdownTotalsTest(unittest.TestCase):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    def test_vote_method_totals(self):
        for csv_file in get_csv_files(VoteBreakdownTotalsTest.root_path):
            short_path = os.path.relpath(csv_file, start=VoteBreakdownTotalsTest.root_path)

            with self.subTest(msg=f"{short_path}"):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    data_test = VoteBreakdownTotals(headers)
                    for row in reader:
                        data_test.test(row)

                self.assertTrue(data_test.passed, data_test.get_failure_message())
