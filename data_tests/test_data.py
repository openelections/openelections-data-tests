import csv
import glob
import os
import unittest
from typing import Iterator

from data_tests.duplicate_entries import DuplicateEntries


def get_csv_files(root_path: str) -> Iterator[str]:
    for file in glob.glob(os.path.join(root_path, "[0-9]" * 4, "**", "*"), recursive=True):
        if file.lower().endswith(".csv"):
            yield file


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

                passed = True
                message = f"\n\n{short_path}"
                if not data_test.passed:
                    passed = False
                    message += f"\n\n* {data_test.get_failure_message()}"

                self.assertTrue(passed, message)
