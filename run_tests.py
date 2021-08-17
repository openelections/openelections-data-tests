import argparse
import unittest

from data_tests.test_data import DuplicateEntriesTest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test", type=str, help="the data test to run")
    parser.add_argument("root_path", type=str, help="the absolute path to the repository containing files to test")
    args = parser.parse_args()

    test_class = None
    if args.test == "duplicate_entries":
        DuplicateEntriesTest.root_path = args.root_path
        test_class = DuplicateEntriesTest
    else:
        raise ValueError(f"Unrecognized data test '{args.test}'.")

    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
    test_runner = unittest.TextTestRunner()
    result = test_runner.run(test_suite)

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)