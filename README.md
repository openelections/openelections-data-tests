[![Build Status](https://github.com/openelections/openelections-data-tests/actions/workflows/unit_tests.yml/badge.svg?branch=master)](https://github.com/openelections/openelections-data-tests/actions)

# OpenElections Data Validation Tests
A collection of tests to validate the contents of OpenElections data files.

## Usage
```
$ python3 run_tests.py <test> <absolute path to data repository>
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

