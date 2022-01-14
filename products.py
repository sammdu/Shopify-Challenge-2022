#!/usr/bin/env python3.9
"""
Enables access to products in the inventory.
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
        - Products.get_all() -> list[sqlite3.Row]
        - Products.get_specific(skus: list) -> list[sqlite3.Row]
        - ...
    """

    db_path: str       # path to a SQLite database file
    table_name: str    # name of the products table

    def __init__(self, db_path: str = ":memory:", table_name: str = 'products') -> None:
        """
        Configure the path to the SQLite database file, defaults to in-memory storage.
        Configure the name of the products table, defaults to 'products'.
        WARNING: table_name is not sanitized!
        """
        self.db_path = db_path
        self.table_name = table_name

    def _get_conn_cur(
        self,
        use_row_factory: bool = False
    ) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        """
        Return SQLite database connaction and cursor objects based on the database path.
        If use_row_factory is set to True, then use sqlite3.Row as the connection's row
        factory.
        """
        conn: sqlite3.Connection = sqlite3.connect(self.db_path)

        if use_row_factory:
            conn.row_factory = sqlite3.Row

        cur: sqlite3.Cursor = conn.cursor()
        return conn, cur

    @staticmethod
    def _sqlite_error_msg(
        context: str,       # the context that led to the error
        error: Exception,   # the error itself
        table_name: str,    # the name of the table being operated on
        extra: str = ''     # any additional information that may be helpful
    ) -> str:
        """
        Create a helpful SQLite error message and return the message as a string.
        """
        additional_info: str = f'\t{extra}\n' if extra else ''
        message: str = ''.join((
            f'\n---\nSQLite\nError occurred while {context}.\n',
            f'\tTable: {table_name}\n{additional_info}{error}\n---'
        ))
        return message

    def create_table(self) -> None:
        """
        Create a products table that can store sku, name, and quantity for each product.
        """
        # create a connection to the database and obtain a cursor
        conn, cur = self._get_conn_cur()

        # SQL statement to create the products table
        stmt = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                sku         TEXT PRIMARY KEY NOT NULL,
                name        TEXT NOT NULL,
                quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
            );
        '''

        # attempt to execute the SQL statement
        try:
            cur.execute(stmt)
            conn.commit()
        except sqlite3.Error as error:
            print(self._sqlite_error_msg(
                context='creating table',
                error=error,
                table_name=self.table_name
            ))

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

        # SQL statement to ingest the given data into the `products` table
        stmt = '''
            INSERT OR IGNORE INTO products(sku, name, quantity)
            VALUES (:sku, :name, :quantity);
        '''

        # attempt to execute the SQL statement
        try:
            cur.executemany(stmt, data)
            conn.commit()
        except sqlite3.Error as error:
            print(self._sqlite_error_msg(
                context='importing data',
                error=error,
                table_name=self.table_name
            ))

        # close the database connection
        conn.close()

    def get_all(self) -> list[sqlite3.Row]:
        """
        Return all products in the products table as a list, where each product is
        represented by a SQLite Row object, and can be used as and converted to a Python
        dictionary.
        """
        # create a connection to the database and obtain a cursor
        conn, cur = self._get_conn_cur(use_row_factory=True)

        # SQL statement to fetch all products
        stmt = f'SELECT * FROM {self.table_name};'

        # attempt to execute the SQL statement and fetch results
        try:
            cur.execute(stmt)
            results = cur.fetchall()
        except sqlite3.Error as error:
            print(self._sqlite_error_msg(
                context='getting all products',
                error=error,
                table_name=self.table_name
            ))

        # close the database connection
        conn.close()

        return results

    def get_specific(self, skus: list) -> list[sqlite3.Row]:
        """
        Return specific products in the products table as a list, identified by their sku,
        and given by the skus parameter.
        Each product is represented by a SQLite Row object, and can be used as and
        converted to a Python dictionary.
        """
        # create a connection to the database and obtain a cursor
        conn, cur = self._get_conn_cur(use_row_factory=True)

        # SQL statement to fetch specific products identified by the given skus
        placeholders = ','.join('?' * len(skus))  # pre-set correct number of placeholders
        stmt = f'SELECT * FROM {self.table_name} WHERE sku IN ({placeholders});'

        # attempt to execute the SQL statement and fetch results
        try:
            cur.execute(stmt, skus)
            results = cur.fetchall()
        except sqlite3.Error as error:
            print(self._sqlite_error_msg(
                context='getting specific products',
                error=error,
                table_name=self.table_name,
                extra=f'Requested products: {skus}'
            ))

        # close the database connection
        conn.close()

        return results


if __name__ == '__main__':
    from csv_utils import csv_to_list
    data = csv_to_list("products_init.csv")
    p = Products(db_path='products.db')
    p.create_table()
    p.import_data(data=data)
    results = p.get_all()
    print([dict(i) for i in results])
    specifics = p.get_specific(['449862', '502318'])
    print([dict(i) for i in specifics])
