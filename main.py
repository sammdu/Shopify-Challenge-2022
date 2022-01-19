#!/usr/bin/env python3.9
"""
Inventory Management System
Shopify 2022 Summer Internship Technical Challenge

Main application entry point. Serves the following endpoints:
    - GET /                         renders and returns the web UI HTML templates
    - GET /export-csv   ?items=     a JSON list of skus to specify products to include in
                                    the returned CSV file; empty list [] for all products
    - 
"""

from flask import Flask, render_template, request, make_response, jsonify, send_file
import json
from csv_utils import csv_to_list, sqlite_rows_to_csv
from products import Products

# global constants
SQLITE_DB_PATH: str = 'products.db'
INITIAL_DATA_CSV: str = 'products_init.csv'
EXPORTED_CSV_PATH: str = 'export.csv'
INVENTORY: Products

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    Render and return the main web UI to the frontend.
    Pass the INVENTORY object to the Jinja2 HTML templates.
    """
    return render_template('index.html', inventory=INVENTORY)


@app.route('/export-csv', methods=['GET'])
def export_csv():
    """
    """
    # try to read the list of items to export from the GET parameter `items`
    try:
        items: list = json.loads(request.args.get('items'))
        assert isinstance(items, list)
    except Exception as err:
        return make_response(
            f"Parameter error! Must provide a JSON list of skus for `items`.\n{err}",
            400
        )

    # get the products specified by items; empty list results in all products being dumped
    dump: list
    if items == []:
        dump = INVENTORY.get_all()
    else:
        dump = INVENTORY.get_specific(skus=items)

    # try to convert the list of SQLite Rows in the dump to a CSV file
    try:
        sqlite_rows_to_csv(dump, path=EXPORTED_CSV_PATH)
    except Exception as err:
        return make_response(
            f"Server could not export the CSV file. Please try again.\n{err}",
            500
        )

    # return the exported items in export.csv as 'inventory_export.csv' to the browser
    return send_file(
        path_or_file=EXPORTED_CSV_PATH,
        mimetype='text/csv',
        as_attachment=True,
        download_name='inventory_export.csv'
    )


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
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # reload the dev server upon HTML changes
    app.run(threaded=True, port=5000, use_reloader=True)
