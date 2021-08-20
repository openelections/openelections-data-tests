import unittest

from data_tests import duplicate_entries


class DuplicateEntriesTest(unittest.TestCase):
    def test_ragged_with_duplicates(self):
        data_test = duplicate_entries.DuplicateEntries(["a", "votes", "c"])
        data_test.test(["a", "b", "c"])
        data_test.test(["a", "b", "c", "d"])
        data_test.test(["a", "b", "c", "d"])
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertIsNotNone(failure_message)
        self.assertNotEqual("", failure_message)

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
        data_test = duplicate_entries.DuplicateEntries(["a", "b", "a_votes_b", "c_votes_d", "e"])
        data_test.test(["a", "b", "c", "d", "e"])
        data_test.test(["d", "e", "f", "g", "h"])
        data_test.test(["a", "b", "cc", "d", "e"])
        data_test.test(["d", "e", "f", "g", "i"])
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertIsNotNone(failure_message)
        self.assertNotEqual("", failure_message)

    def test_without_duplicates(self):
        data_test = duplicate_entries.DuplicateEntries(["a", "b", "a_votes_b", "c_votes_d", "e"])
        data_test.test(["a", "b", "c", "d", "e"])
        data_test.test(["ab", "", "c", "d", "e"])
        data_test.test(["a", "b", "c", "de", ""])
        data_test.test(["", "", "", "", ""])
        data_test.test(["", "", "", "", ""])
        self.assertTrue(data_test.passed)
