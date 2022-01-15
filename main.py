#!/usr/bin/env python3.9
"""
Inventory Management System
Shopify 2022 Summer Internship Technical Challenge

Main application entry point. Serves the following endpoints:
    - GET /     renders and returns the web UI HTML templates
"""

from flask import Flask, render_template, request, make_response, jsonify, session
from csv_utils import csv_to_list
from products import Products

# global constants
SQLITE_DB_PATH: str = 'products.db'
INITIAL_DATA_CSV: str = 'products_init.csv'
INVENTORY: Products

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    """
    return render_template('index.html', inventory=INVENTORY)


if __name__ == '__main__':
    from pathlib import Path

    # create the inventory object
    INVENTORY = Products(db_path=SQLITE_DB_PATH, table_name='products')

    # create a new products table if the database file did not exist before
    if not Path(SQLITE_DB_PATH).is_file():
        INVENTORY.create_table()
        # ingest initial product data if the INITIAL_DATA_CSV file exists
        if Path(INITIAL_DATA_CSV).is_file():
            initial_data: list = csv_to_list(INITIAL_DATA_CSV)
            INVENTORY.import_data(data=initial_data)

    # run the Flask development server
    app.run(threaded=True, port=5000)
