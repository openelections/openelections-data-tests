import argparse
import unittest

from data_tests.test_data import DuplicateEntriesTest, TruncatedTestResult


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test", type=str, help="the data test to run")
    parser.add_argument("root_path", type=str, help="the absolute path to the repository containing files to test")
    parser.add_argument("--log-file", type=str, help="the absolute path to a file that the full failure messages will "
                                                     "be written to")
    parser.add_argument("--max-console-lines", type=int, help="the maximum number of lines of a failure message to "
                                                              "print to the console")
    args = parser.parse_args()

    if args.log_file is not None:
        TruncatedTestResult.log_file = args.log_file
    if args.max_console_lines is not None:
        TruncatedTestResult.max_console_lines = args.max_console_lines

    test_class = None
    if args.test == "duplicate_entries":
        DuplicateEntriesTest.root_path = args.root_path
        test_class = DuplicateEntriesTest
    else:
        raise ValueError(f"Unrecognized data test '{args.test}'.")

    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
    test_runner = unittest.TextTestRunner(resultclass=TruncatedTestResult)
    result = test_runner.run(test_suite)

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
