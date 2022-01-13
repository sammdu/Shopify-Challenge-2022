#!/usr/bin/env python3.9
"""
Allows for project-relevant SQLite database access by exposing the Products class.
"""

import sqlite3


class Products:
    """
    A class that specifies the schema of the products table and implements methods for
    operating on products in the inventory system.

    Public methods:
        - Products(db_path: str = ":memory:", table_name: str = 'products') -> None
        - Products.create_table() -> None
        - Products.import_data(data: list[dict]) -> None
        - ...
    """

    db_path: str       # path to a SQLite database file
    table_name: str    # name of the products table

    def __init__(self, db_path: str = ":memory:", table_name: str = 'products') -> None:
        """
        Configure the path to the SQLite database file, defaults to in-memory storage.
        Configure the name of the products table, defaults to 'products'.
        """
        self.db_path = db_path
        self.table_name = table_name

    def _get_conn_cur(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        """
        Return SQLite database connaction and cursor objects based on the database path.
        """
        conn: sqlite3.Connection = sqlite3.connect(self.db_path)
        cur: sqlite3.Cursor = conn.cursor()
        return conn, cur

    def create_table(self) -> None:
        """
        Create a products table that can store sku, name, and quantity for each product.
        """
        # create a connection to the database and obtain a cursor
        conn, cur = self._get_conn_cur()

        # create the products table
        stmt = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                sku         TEXT PRIMARY KEY NOT NULL,
                name        TEXT NOT NULL,
                quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
            );
        '''
        try:
            cur.execute(stmt)
            conn.commit()
        except sqlite3.Error as error:
            print(
                '---\nSQLite',
                f'\nError occurred while creating table `{self.table_name}`:\n{error}\n---'
            )

        # close the database connection
        conn.close()

    def import_data(self, data: list[dict]) -> None:
        """
        Given a list of dictionaries, insert each dictionary as a row in the products
        table. Each dictionary must contain keys that correspond to column names of the
        products table.
        When a conflict occurrs, ignore the conflict and skip that row.
        """
        # create a connection to the database and obtain a cursor
        conn, cur = self._get_conn_cur()

        # ingest the given data into the `products` table
        stmt = '''
            INSERT OR IGNORE INTO products(sku, name, quantity)
            VALUES (:sku, :name, :quantity);
        '''
        try:
            cur.executemany(stmt, data)
            conn.commit()
        except sqlite3.Error as error:
            print(
                '---\nSQLite',
                f'\nError occurred while importing data into table `{self.table_name}`:',
                f'\n{error}\n---'
            )

        # close the database connection
        conn.close()

    def export_all(self) -> list[dict]:
        """

        """

    def export_specific(self, skus: list) -> list[dict]:
        """

        """


if __name__ == '__main__':
    from csv_utils import csv_to_list
    data = csv_to_list("products_init.csv")
    p = Products(db_path='products.db')
    p.create_table()
    p.import_data(data=data)
