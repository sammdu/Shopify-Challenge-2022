#!/usr/bin/env python3.9
"""
Utility functions that allows for the project-relevant interactions
with CSV files.
"""

import csv


def csv_to_list(path: str) -> list[dict]:
    """
    Given a path to a CSV file, return a list of dictionaries representing
    the contents of the CSV file.
    """
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)
