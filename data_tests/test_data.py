import csv
import glob
import logging
import os
import unittest
from typing import Iterator

from data_tests.duplicate_entries import DuplicateEntries


def get_csv_files(root_path: str) -> Iterator[str]:
    for file in glob.glob(os.path.join(root_path, "[0-9]" * 4, "**", "*"), recursive=True):
        if file.lower().endswith(".csv"):
            yield file


def _get_logger(name: str, log_file: str) -> logging.Logger:
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


def _log_failure(logger: logging.Logger, description: str, message: str):
    if logger is not None:
        logger.debug("======================================================================")
        logger.debug(f"FAIL: {description}")
        logger.debug("----------------------------------------------------------------------")
        logger.debug(f"{message}\n")


class DuplicateEntriesTest(unittest.TestCase):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    log_file = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if DuplicateEntriesTest.log_file is None:
            self.__logger = None
        else:
            self.__logger = _get_logger("Duplicate Entries", DuplicateEntriesTest.log_file)

    def __assertTrue(self, result: bool, description: str, short_message: str, full_message: str):
        if not result:
            _log_failure(self.__logger, description, full_message)
        self.assertTrue(result, short_message)

    def test_duplicate_entries(self):
        for csv_file in get_csv_files(DuplicateEntriesTest.root_path):
            short_path = os.path.relpath(csv_file, start=DuplicateEntriesTest.root_path)

            with self.subTest(msg=f"{short_path}"):
                data_test = DuplicateEntries()
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    for row in reader:
                        data_test.test(row)

                short_message = data_test.get_failure_message(max_examples=10)
                full_message = data_test.get_failure_message()
                self.__assertTrue(data_test.passed, f"{self} [{short_path}]", short_message, full_message)
