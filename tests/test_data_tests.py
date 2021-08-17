import unittest

from data_tests import duplicate_entries


class DuplicateEntriesTest(unittest.TestCase):
    def test_with_duplicates(self):
        data_test = duplicate_entries.DuplicateEntries()
        data_test.test(["a", "b", "c"])
        data_test.test(["d", "e", "f"])
        data_test.test(["a", "b", "c"])
        data_test.test(["g", "h", "i"])
        self.assertFalse(data_test.passed)

        failure_message = data_test.get_failure_message()
        self.assertIsNotNone(failure_message)
        self.assertNotEqual("", failure_message)

    def test_without_duplicates(self):
        data_test = duplicate_entries.DuplicateEntries()
        data_test.test(["a", "b", "c"])
        data_test.test(["ab", "", "c"])
        data_test.test(["", "a", "b", "c"])
        data_test.test(["a", "b", "c", ""])
        data_test.test(["", "", ""])
        data_test.test(["", "", ""])
        self.assertTrue(data_test.passed)
