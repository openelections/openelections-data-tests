[![Build Status](https://github.com/openelections/openelections-data-tests/actions/workflows/unit_tests.yml/badge.svg?branch=main)](https://github.com/openelections/openelections-data-tests/actions)

# OpenElections Data Validation Tests
A collection of tests to validate the contents of OpenElections data files.

## Usage
```
usage: run_tests.py [-h] [--log-file LOG_FILE] [--max-console-lines MAX_CONSOLE_LINES] test root_path

positional arguments:
  test                  the data test to run
  root_path             the absolute path to the repository containing files to test

optional arguments:
  -h, --help            show this help message and exit
  --log-file LOG_FILE   the absolute path to a file that the full failure messages will be written to
  --max-console-lines MAX_CONSOLE_LINES
                        the maximum number of lines of a failure message to print to the console
```

The data are expected to be contained in CSV files that reside under
directories named by the corresponding election years.  For example,

```
<data repository>
|
|-- 2000
|   |-- a.csv
|   |-- b.csv
|-- 2001
    |-- counties
        |-- c.csv
        |-- d.csv
        |-- e.csv
```

## Available Tests
* `duplicate_entries` detects the presence of duplicated entries.

