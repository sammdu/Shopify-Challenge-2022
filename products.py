#!/usr/bin/env python3.9
"""

"""

import sqlite3


class Products:
    """
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """

        """
        self.db_path = db_path

    def _get_db_conn(self) -> sqlite3.Connection:
        """

        """
        return sqlite3.connect(self.db_path)

    def import_products(self, data: list[dict]) -> None:
        """

        """

    def export_all_products(self) -> list[dict]:
        """

        """

    def export_specific_products(self, skus: list) -> list[dict]:
        """

        """
