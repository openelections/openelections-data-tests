[![Build Status](https://github.com/openelections/openelections-data-tests/actions/workflows/unit_tests.yml/badge.svg?branch=main)](https://github.com/openelections/openelections-data-tests/actions/workflows/unit_tests.yml?query=branch%3Amain)

# OpenElections Data Validation Tests
A collection of tests to validate the contents of OpenElections data files.

## Usage
```
usage: run_tests.py [-h] [--log-file LOG_FILE] {duplicate_entries,missing_values,vote_breakdown_totals} root_path

positional arguments:
  {duplicate_entries,missing_values,vote_breakdown_totals}
                        the data test to run
  root_path             the absolute path to the repository containing files to test

optional arguments:
  -h, --help            show this help message and exit
  --log-file LOG_FILE   the absolute path to a file that the full failure messages will be written to
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
* `vote_breakdown_totals` detects entries where the sum of the broken down votes (e.g., `absentee`, `early_voting`, `election_day`, `mail`, `provisional`) is greater than the total `votes`.
* `missing_values` verifies that required values are not missing.
