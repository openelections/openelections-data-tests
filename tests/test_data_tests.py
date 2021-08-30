import re
import unittest

from data_tests import duplicate_entries, inconsistencies


class DuplicateEntriesTest(unittest.TestCase):
    def test_ragged_with_duplicates(self):
        rows = [
            ["header 1", "votes", "header 3", "early_voting", "election_day", "mail", "provisional", "absentee"],
            ["a", "b", "", "d", "e", "f", "g", "h"],
            ["a", "b", "c", "d"],
            ["a", "b", "c", "d"]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "1 duplicate entries")
        self.assertNotRegex(failure_message, "Row 1.*")
        self.assertNotRegex(failure_message, "Row 2.*")
        self.assertRegex(failure_message, "Row 3.*" + re.escape(f"{rows[2]}"))
        self.assertRegex(failure_message, "Row 4.*" + re.escape(f"{rows[3]}"))

    def test_ragged_without_duplicates(self):
        rows = [
            ["header 1", "votes", "header 3", "early_voting", "election_day", "mail", "provisional", "absentee"],
            ["a", "b", "c", "d", "e", "f", "g", "h"],
            ["a", "b", "cc", "d", "e", "f", "g", "h"],
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
            [
                "header 1", "header 2", "a_votes_b", "c_votes_d", "early_voting", "election_day", "mail",
                "provisional", "absentee"
            ],
            ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
            ["d", "e", "f", "g", "e", "f", "g", "h", "i"],
            ["a", "b", "cc", "d", "ee", "f", "gg", "h", "i"],
            ["a", "b", "c", "dd", "e", "ff", "g", "hh", "i"],
            ["a", "b", "c", "dd", "e", "ff", "g", "h", "ii"],
            ["d", "ee", "f", "g", "e", "f", "g", "h", "i"]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "3 duplicate entries")
        self.assertNotRegex(failure_message, "Row 1.*")
        self.assertRegex(failure_message, "Row 2.*" + re.escape(f"{rows[1]}"))
        self.assertNotRegex(failure_message, "Row 3.*")
        self.assertRegex(failure_message, "Row 4.*" + re.escape(f"{rows[3]}"))
        self.assertRegex(failure_message, "Row 5.*" + re.escape(f"{rows[4]}"))
        self.assertRegex(failure_message, "Row 6.*" + re.escape(f"{rows[5]}"))
        self.assertNotRegex(failure_message, "Row 7.*")

    def test_without_duplicates(self):
        rows = [
            [
                "header 1", "header 2", "a_votes_b", "header 5", "early_voting", "election_day", "mail",
                "provisional", "absentee"
            ],
            ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
            ["ab", "", "c", "d", "e", "f", "g", "h", "i"],
            ["a", "b", "c", "de", "", "f", "g", "h", "i"],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""]
        ]

        data_test = duplicate_entries.DuplicateEntries(rows[0])
        for row in rows:
            data_test.test(row)
        self.assertTrue(data_test.passed)


class VoteBreakdownTotalsTest(unittest.TestCase):
    def test_consistent(self):
        headers = ["header", "provisional", "mail", "votes", "early_voting", "election_day", "absentee"]
        rows = [
            ["a", "1", "2", "15", "3", "4", "5"],
            ["a", "2", "1", "16", "3", "4", "5"],
            ["a", "1", "2", "15.0", "0", "7", "5"],
            ["a", "", "3", "15", "3", "4", "5"],
            ["a", "b", "3", "16", "3", "4", "5"],
            ["a", "", "", "15", "", "", "5"],
            ["a", "1", "2", "*", "3", "4", "5"],
            ["a", "1", "2", "", "3", "4", "5"],
            ["a", "10", "2", "10", "3", "4", "5", "5"]
        ]

        data_test = inconsistencies.VoteBreakdownTotals(headers)
        for row in rows:
            data_test.test(row)
        self.assertTrue(data_test.passed)

    def test_inconsistent(self):
        headers = ["header", "provisional", "mail", "votes", "early_voting", "election_day", "absentee"]
        rows = [
            ["a", "1", "3", "15", "3", "4", "5"],
            ["a", "1", "2", "15", "3", "4", "5"],
            ["a", "", "2", "13", "3", "4", "5"]
        ]

        data_test = inconsistencies.VoteBreakdownTotals(headers)
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "2 rows")
        self.assertRegex(failure_message, "Row 1.*" + re.escape(f"{rows[0]}"))
        self.assertNotRegex(failure_message, "Row 2.*")
        self.assertRegex(failure_message, "Row 3.*" + re.escape(f"{rows[2]}"))

    def test_missing_votes_header(self):
        headers = ["header", "provisional", "mail", "early_voting", "election_day"]
        data_test = inconsistencies.VoteBreakdownTotals(headers)
        data_test.test(["a", "1", "8", "3", "4"])
        self.assertTrue(data_test.passed)
