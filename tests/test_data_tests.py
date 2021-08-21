import re
import unittest

from data_tests import duplicate_entries


class DuplicateEntriesTest(unittest.TestCase):
    def test_ragged_with_duplicates(self):
        rows = [
            ["header 1", "votes", "header 3"],
            ["a", "b", "c"],
            ["a", "b", "c", "d"],
            ["a", "b", "c", "d"]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "1 duplicate row")
        self.assertRegex(failure_message, "Row 3.*" + re.escape(f"{rows[2]}"))
        self.assertRegex(failure_message, "Row 4.*" + re.escape(f"{rows[3]}"))

    def test_ragged_without_duplicates(self):
        rows = [
            ["header 1", "votes", "header 3"],
            ["a", "b", "c"],
            ["a", "b", "c", "d"],
            ["a", "b", "d", "e"],
            ["", "a", "b", "d", "e"],
            ["a", "b", "d", "e", ""],
            ["", ""],
            ["", ""]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertTrue(data_test.passed)

    def test_with_duplicates(self):
        rows = [
            ["header 1", "header 2", "a_votes_b", "c_votes_d", "header 5"],
            ["a", "b", "c", "d", "e"],
            ["d", "e", "f", "g", "h"],
            ["a", "b", "cc", "d", "e"],
            ["a", "b", "c", "dd", "e"],
            ["d", "e", "f", "g", "i"]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "2 duplicate row")
        self.assertRegex(failure_message, "Row 2.*" + re.escape(f"{rows[1]}"))
        self.assertRegex(failure_message, "Row 4.*" + re.escape(f"{rows[3]}"))
        self.assertRegex(failure_message, "Row 5.*" + re.escape(f"{rows[4]}"))

    def test_without_duplicates(self):
        rows = [
            ["header 1", "header 2", "a_votes_b", "c_votes_d", "header 5"],
            ["a", "b", "c", "d", "e"],
            ["ab", "", "c", "d", "e"],
            ["a", "b", "c", "de", ""],
            ["", "", "", "", ""],
            ["", "", "", "", ""]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertTrue(data_test.passed)
