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


def sqlite_rows_to_csv(results: list[Row], path: str) -> None:
    """
    Given a list of SQLite Row objects and a file path, write the list of Rows into a CSV
    file specified by the path. Each Row is a row in the CSV file.
    CSV headers:
        sku,name,quantity
    """
    headers: list = ['sku', 'name', 'quantity']
    with open(path, 'w', newline='') as file:
        writer: csv.DictWriter = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dict(i) for i in results)
