[![Build Status](https://github.com/openelections/openelections-data-tests/actions/workflows/unit_tests.yml/badge.svg?branch=main)](https://github.com/openelections/openelections-data-tests/actions/workflows/unit_tests.yml?query=branch%3Amain)

# OpenElections Data Validation Tests
A collection of tests to validate the contents of OpenElections data files.

## Usage
```
usage: run_tests.py [-h] [--group-failures] [--log-file LOG_FILE] [--max-examples N] {duplicate_entries,missing_values,vote_breakdown_totals} root_path

positional arguments:
  {duplicate_entries,missing_values,vote_breakdown_totals}
                        the data test to run
  root_path             the absolute path to the repository containing files to test

optional arguments:
  -h, --help            show this help message and exit
  --group-failures      group the failures by year in the console output using the GitHub Actions group and endgroup workflow commands
  --log-file LOG_FILE   the absolute path to a file that the full failure messages will be written to
  --max-examples N      the maximum number of failing rows to print to the console. If a negative value is provided, all failures will be printed.
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
* `duplicate_entries` detects the presence of duplicate entries.
* `vote_breakdown_totals` detects entries where the sum of the broken down votes (e.g., `absentee`, `early_voting`, `election_day`, `mail`, `provisional`) is greater than the total `votes`.  If the column headers match some known schemas, then the values are compared for equality.
* `missing_values` verifies that required values are not missing.
