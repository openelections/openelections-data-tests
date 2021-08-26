import argparse
import unittest

from data_tests.test_data import DuplicateEntriesTest, TestCase, VoteBreakdownTotalsTest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test", type=str, help="the data test to run")
    parser.add_argument("root_path", type=str, help="the absolute path to the repository containing files to test")
    parser.add_argument("--log-file", type=str, help="the absolute path to a file that the full failure messages will "
                                                     "be written to")
    args = parser.parse_args()

    TestCase.root_path = args.root_path
    TestCase.log_file = args.log_file

    test_class = None
    if args.test == "duplicate_entries":
        test_class = DuplicateEntriesTest
    elif args.test == "vote_breakdown_totals":
        VoteBreakdownTotalsTest.root_path = args.root_path
        test_class = VoteBreakdownTotalsTest
    else:
        raise ValueError(f"Unrecognized data test '{args.test}'.")

    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
    test_runner = unittest.TextTestRunner()
    result = test_runner.run(test_suite)

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
