import re
import unittest

from data_tests import duplicate_entries


class DuplicateEntriesTest(unittest.TestCase):
    def test_ragged_with_duplicates(self):
        rows = [
            ["a", "votes", "c"],
            ["a", "b", "c"],
            ["a", "b", "c", "d"],
            ["a", "b", "c", "d"]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows[1:]:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "1 duplicate row")
        self.assertRegex(failure_message, "Row 2.*" + re.escape(f"{rows[2]}"))
        self.assertRegex(failure_message, "Row 3.*" + re.escape(f"{rows[3]}"))

    def test_ragged_without_duplicates(self):
        data_test = duplicate_entries.DuplicateEntries(["a", "votes", "c"])
        data_test.test(["a", "b", "c"])
        data_test.test(["a", "b", "c", "d"])
        data_test.test(["a", "b", "d", "e"])
        data_test.test(["", "a", "b", "d", "e"])
        data_test.test(["a", "b", "d", "e", ""])
        data_test.test(["", ""])
        data_test.test(["", ""])
        self.assertTrue(data_test.passed)

    def test_with_duplicates(self):
        rows = [
            ["a", "b", "a_votes_b", "c_votes_d", "e"],
            ["a", "b", "c", "d", "e"],
            ["d", "e", "f", "g", "h"],
            ["a", "b", "cc", "d", "e"],
            ["a", "b", "c", "dd", "e"],
            ["d", "e", "f", "g", "i"]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows[1:]:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "2 duplicate row")
        self.assertRegex(failure_message, "Row 1.*" + re.escape(f"{rows[1]}"))
        self.assertRegex(failure_message, "Row 3.*" + re.escape(f"{rows[3]}"))
        self.assertRegex(failure_message, "Row 4.*" + re.escape(f"{rows[4]}"))

    def test_without_duplicates(self):
        data_test = duplicate_entries.DuplicateEntries(["a", "b", "a_votes_b", "c_votes_d", "e"])
        data_test.test(["a", "b", "c", "d", "e"])
        data_test.test(["ab", "", "c", "d", "e"])
        data_test.test(["a", "b", "c", "de", ""])
        data_test.test(["", "", "", "", ""])
        data_test.test(["", "", "", "", ""])
        self.assertTrue(data_test.passed)
