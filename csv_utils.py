#!/usr/bin/env python3.9
"""
Utility functions that allow for the project-relevant interactions with CSV files.
"""

import csv
from sqlite3 import Row


def csv_to_list(path: str) -> list[dict]:
    """
    Given a path to a CSV file, return a list of dictionaries representing
    the contents of the CSV file, with keys being the headers, and values
    being the contents of each row.
    """
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)


def sqlite_rows_to_csv(results: Row) -> None:
    """

    """
