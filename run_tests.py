import argparse
import unittest

from data_tests.test_data import DuplicateEntriesTest, MissingValuesTest, TestCase, VoteBreakdownTotalsTest, TestResult

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test", choices=["duplicate_entries", "missing_values", "vote_breakdown_totals"], type=str,
                        help="the data test to run")
    parser.add_argument("root_path", type=str, help="the absolute path to the repository containing files to test")
    parser.add_argument("--group-failures", action="store_true",
                        help="group the failures by year in the console output using the GitHub Actions group and "
                             "endgroup workflow commands")
    parser.add_argument("--log-file", type=str, help="the absolute path to a file that the full failure messages will "
                                                     "be written to")
    parser.add_argument("--max-examples", type=int, default=10, metavar="N",
                        help="the maximum number of failing rows to print to the console. If a negative value is "
                             "provided, all failures will be printed.")
    args = parser.parse_args()

    TestCase.root_path = args.root_path
    TestCase.log_file = args.log_file
    TestCase.max_examples = args.max_examples

    test_class = None
    if args.test == "duplicate_entries":
        test_class = DuplicateEntriesTest
    elif args.test == "missing_values":
        test_class = MissingValuesTest
    elif args.test == "vote_breakdown_totals":
        test_class = VoteBreakdownTotalsTest
    else:
        raise ValueError(f"Unrecognized data test '{args.test}'.")

    result_class = TestResult if args.group_failures else None
    test_runner = unittest.TextTestRunner(resultclass=result_class)
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
    result = test_runner.run(test_suite)

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
