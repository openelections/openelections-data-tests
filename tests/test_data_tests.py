import csv
import os
import re
import subprocess
import tempfile
import unittest

from data_tests import duplicate_entries, inconsistencies, missing_values


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


# noinspection DuplicatedCode
class MissingValueTest(unittest.TestCase):
    def test_empty(self):
        headers = ["a", "b", "c"]
        rows = [
            ["1", "2", "3"],
            ["1", "", "3"],
            ["1", "2", "3"]
        ]

        data_test = missing_values.MissingValue("b", headers)
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "1 rows")
        self.assertNotRegex(failure_message, "Row 1.*")
        self.assertRegex(failure_message, "Row 2.*" + re.escape(f"{rows[1]}"))
        self.assertNotRegex(failure_message, "Row 3.*")

    def test_index_out_of_range(self):
        headers = ["a", "b", "c"]
        rows = [
            ["1", "2", "3"],
            ["1"]
        ]

        data_test = missing_values.MissingValue("b", headers)
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "1 rows")
        self.assertNotRegex(failure_message, "Row 1.*")
        self.assertRegex(failure_message, "Row 2.*" + re.escape(f"{rows[1]}"))

    def test_not_applicable(self):
        headers = ["a", "b", "c"]
        rows = [
            ["1", "", "3"],
            ["1", " ", "3"]
        ]

        data_test = missing_values.MissingValue("d", headers)
        for row in rows:
            data_test.test(row)
        self.assertTrue(data_test.passed)

    def test_not_missing(self):
        headers = ["a", "b", "c"]
        rows = [
            ["1", "2", "3"],
            ["1", " 2", "3"],
            ["1", "2 ", "3"]
        ]

        data_test = missing_values.MissingValue("b", headers)
        for row in rows:
            data_test.test(row)
        self.assertTrue(data_test.passed)

    def test_whitespace(self):
        headers = ["a", "b", "c"]
        rows = [
            ["1", "2", "3"],
            ["1", " \n\t", "3"],
            ["1", "2", "3"]
        ]

        data_test = missing_values.MissingValue("b", headers)
        for row in rows:
            data_test.test(row)
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertRegex(failure_message, "1 rows")
        self.assertNotRegex(failure_message, "Row 1.*")
        self.assertRegex(failure_message, "Row 2.*" + re.escape(f"{rows[1]}"))
        self.assertNotRegex(failure_message, "Row 3.*")


class RunTestsTest(unittest.TestCase):
    bad_data_dir = None
    bad_rows = [
        ["county", "precinct", "absentee", "votes"],
        ["a", "b", "1", "2"],
        ["a", "b", "2", "3"],  # Duplicate of row 1
        ["", "c", "1", "2"],  # Missing county
        ["c", "d", "3", "2"],  # Vote breakdown totals > votes
    ]
    good_data_dir = None
    good_rows = [
        ["county", "precinct", "absentee", "votes"],
        ["a", "b", "1", "2"],
        ["c", "d", "2", "3"],
    ]
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    year = "2020"

    @staticmethod
    def create_data(root_path, year, rows):
        year_dir = os.path.join(root_path, year)
        os.mkdir(year_dir)
        _, csv_file_path = tempfile.mkstemp(suffix=".csv", dir=year_dir, text=True)
        with open(csv_file_path, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)

    @classmethod
    def setUpClass(cls):
        cls.bad_data_dir = tempfile.TemporaryDirectory()
        RunTestsTest.create_data(cls.bad_data_dir.name, cls.year, cls.bad_rows)

        cls.good_data_dir = tempfile.TemporaryDirectory()
        RunTestsTest.create_data(cls.good_data_dir.name, cls.year, cls.good_rows)

    def setUp(self):
        self.log_file = tempfile.NamedTemporaryFile(dir=self.bad_data_dir.name)

    def run_test(self, test, root_path, *args):
        command = ["python", os.path.join(RunTestsTest.root_path, "run_tests.py"), test,
                   f"--log-file={self.log_file.name}"]
        command.extend(args)
        command.append(root_path)
        completed_process = subprocess.run(command, capture_output=True)
        return completed_process

    def test_duplicate_entries(self):
        self.verify_success("duplicate_entries")
        self.verify_failure("duplicate_entries", "1 duplicate entries", [2, 3])

    def test_group_failures(self):
        completed_process = self.run_test("duplicate_entries", self.bad_data_dir.name)
        ungrouped_output = completed_process.stderr.decode()
        self.assertNotRegex(ungrouped_output, "::group::")
        self.assertNotRegex(ungrouped_output, "::endgroup::")

        ungrouped_lines = ungrouped_output.splitlines()
        bad_row_indices = [i for i, row in enumerate(ungrouped_lines) if re.search("Row", row)]
        expected_group_body = "\n".join(ungrouped_lines[:bad_row_indices[-1] + 1])

        completed_process = self.run_test("duplicate_entries", self.bad_data_dir.name, "--group-failures")
        grouped_output = completed_process.stderr.decode()
        self.assertRegex(grouped_output, rf"::group::{self.year}\s*{re.escape(expected_group_body)}\s*::endgroup::")

    def test_missing_values(self):
        self.verify_success("missing_values")
        self.verify_failure("missing_values", "1 rows.*missing.*county", [4])

    def test_vote_breakdown_totals(self):
        self.verify_success("vote_breakdown_totals")
        self.verify_failure("vote_breakdown_totals", "1 rows.*absentee.*", [5])

    def verify_success(self, test):
        self.assertEqual(0, self.run_test(test, self.good_data_dir.name).returncode)

    def verify_failure(self, test, expected_message, expected_rows):
        self.assertEqual(1, self.run_test(test, self.bad_data_dir.name).returncode)

        with open(self.log_file.name, "r") as log_file:
            log_file_contents = "\n".join(log_file.readlines())

        self.assertRegex(log_file_contents, expected_message)
        for i in range(1, len(self.bad_rows) + 1):
            if i in expected_rows:
                self.assertRegex(log_file_contents, f"Row {i}.*" + re.escape(f"{self.bad_rows[i - 1]}"))
            else:
                self.assertNotRegex(log_file_contents, f"Row {i}.*")


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

    def test_skip_aggregate_rows(self):
        headers = ["candidate", "votes", "mail"]
        data_test = inconsistencies.VoteBreakdownTotals(headers)
        data_test.test(["Total Over / Under", "-1", "0"])
        data_test.test(["Under/ Over Votes", "-1", ""])
        self.assertTrue(data_test.passed)
