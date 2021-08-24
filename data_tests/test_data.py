import csv
import glob
import os
import traceback
import unittest
from typing import Iterator

from data_tests.duplicate_entries import DuplicateEntries


def get_csv_files(root_path: str) -> Iterator[str]:
    for file in glob.glob(os.path.join(root_path, "[0-9]" * 4, "**", "*"), recursive=True):
        if file.lower().endswith(".csv"):
            yield file


class TruncatedTestResult(unittest.TextTestResult):
    log_file = None
    max_console_lines = float("inf")

    def addSubTest(self, test, subtest, outcome):
        # If outcome is None, the subtest succeeded. Otherwise, it failed with an exception where outcome is a tuple
        # of the form returned by sys.exc_info(): (type, value, traceback).
        if outcome is None:
            super().addSubTest(test, subtest, outcome)
        else:
            # Add the truncated message to the list of failures, but keep the original for the log file.
            original_message = "".join(traceback.format_exception(outcome[0], outcome[1], outcome[2], 0))
            original_message_list = original_message.splitlines()
            extra_lines = len(original_message_list) - TruncatedTestResult.max_console_lines
            if extra_lines > 0:
                new_message_list = original_message_list[:TruncatedTestResult.max_console_lines]
                new_message_list.append(f"[Truncated {extra_lines} lines]")
                new_message = "\n".join(new_message_list)
            else:
                new_message = original_message

            super().addSubTest(test, subtest, (outcome[0], AssertionError(new_message), outcome[2]))

            if TruncatedTestResult.log_file is not None:
                with open(TruncatedTestResult.log_file, "a") as file:
                    file.write("======================================================================\n")
                    file.write(f"FAIL: {subtest}\n")
                    file.write("======================================================================\n")
                    file.write(f"{original_message}\n\n")


class DuplicateEntriesTest(unittest.TestCase):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    def test_duplicate_entries(self):
        for csv_file in get_csv_files(DuplicateEntriesTest.root_path):
            short_path = os.path.relpath(csv_file, start=DuplicateEntriesTest.root_path)

            with self.subTest(msg=f"{short_path}"):
                data_test = DuplicateEntries()
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    for row in reader:
                        data_test.test(row)

                self.assertTrue(data_test.passed, data_test.get_failure_message())
