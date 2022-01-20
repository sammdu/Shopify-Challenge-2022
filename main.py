#!/usr/bin/env python3.9
"""
Inventory Management System
Shopify 2022 Summer Internship Technical Challenge

Main application entry point.
Serves the following endpoints:
    - GET       /                           > Renders and returns the web UI HTML templates
    - GET       /get-inventory              > Renders and returns the inventory table HTML
    - GET       /export-csv?items=          > Return a CSV file of the specified products;
                                            empty list [] for all products
    - POST      /import_csv                 > Accept a CSV file and import its contents to
                                            the product inventory
    - POST      /add-product                > Add a new product to the inventory
    - DELETE    /delete-products?items=     > Delete a non-empty list of items from the
                                            inventory
    - POST      /change-name                > Chage the name of a specified product
    - POST      /update-quantity            > Update the quantity of a specified product
"""
# external libraries
from flask import Flask, render_template, request, Response, make_response, send_file
from pathlib import Path

# internal modules
from modules.csv_utils import csv_to_list
from modules.products import Products
import modules.services as services

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


@app.route('/get-inventory', methods=['GET'])
def get_inventory():
    """
    Return the latest inventory table HTML.
    """
    # return the HTML for the latest inventory list
    return render_template('inventory.html', inventory=INVENTORY)


@app.route('/export-csv', methods=['GET'])
def export_csv():
    """
    Return a CSV file of the specified products given by the `items` parameter.
    `items` must be a JSON list of strings, where each string is a unique product SKU.
    If successful, returns `inventory_export.csv`.
    """
    # call the export CSV service to perform the export operation
    resp: Response = services.export_csv(
        inventory=INVENTORY,
        items_param=request.args.get('items'),
        path=EXPORTED_CSV_PATH
    )

    # if export unsuccessful, return the error response and write to terminal
    if resp.status_code != 200:
        return resp

    # return the exported items in EXPORTED_CSV_PATH as 'inventory_export.csv' to the user
    return send_file(
        path_or_file=EXPORTED_CSV_PATH,
        mimetype='text/csv',
        as_attachment=True,
        download_name='inventory_export.csv'
    )


@app.route('/import-csv', methods=['POST'])
def import_csv():
    """
    When given a multipart form POST request, accept a CSV file and import its contents to
    the product inventory.
    When given a GET request,
    """
    # ensure the request is a multipart form data with a file part
    if 'file' not in request.files:
        return make_response("Must provide file as a multipart form request.", 400)

    # call the import CSV service to perform the import operation
    resp: Response = services.import_csv(
        inventory=INVENTORY,
        post_file=request.files['file']
    )
    return resp


@app.route('/add-product', methods=['POST'])
def add_product():
    """
    Adds a new product in the inventory.
    JSON body format:
    {
        'sku': str,
        'name': str,
        'quantity': int
    }
    'quantity' >= 0
    """
    request_data: dict = request.get_json()

    # call the add product service to insert the new product
    resp: Response = services.add_product(
        inventory=INVENTORY,
        sku=request_data['sku'],
        name=request_data['name'],
        quantity=request_data['quantity']
    )

    return resp


@app.route('/delete-products', methods=['DELETE'])
def delete_products():
    """
    Delete the specified products given by the `items` parameter.
    `items` must be a JSON list of strings, where each string is a unique product SKU.
    """
    # call the delete products service to remove the specified product
    resp: Response = services.delete_products(
        inventory=INVENTORY,
        items_param=request.args.get('items')
    )

    return resp


@app.route('/change-name', methods=['POST'])
def change_name():
    """
    Changes the name of the product identified by the SKU.
    JSON body format:
    {
        'sku': str,
        'new_name': str
    }
    """
    request_data: dict = request.get_json()

    # call the change name service to rename the specified product
    resp: Response = services.change_name(
        inventory=INVENTORY,
        sku=request_data['sku'],
        new_name=request_data['new_name']
    )

    return resp


@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    """
    Updates the quantity of the product identified by the SKU.
    JSON body format:
    {
        'sku': str,
        'operation': str,
        'count': int
    }
    'operation' in {'add', 'subtract', 'set'}
    'count' >= 0
    """
    request_data: dict = request.get_json()

    # call the change name service to rename the specified product
    resp: Response = services.update_quantity(
        inventory=INVENTORY,
        sku=request_data['sku'],
        operation=request_data['operation'],
        count=request_data['count']
    )

    return resp


if __name__ == '__main__':
    # create the inventory object
    INVENTORY = Products(db_path=SQLITE_DB_PATH, table_name='products')

    # create a new products table if the database file did not exist before
    if not Path(SQLITE_DB_PATH).is_file():
        INVENTORY.create_table()
        # ingest initial product data if the INITIAL_DATA_CSV file exists
        if Path(INITIAL_DATA_CSV).is_file():
            initial_data: list = csv_to_list(INITIAL_DATA_CSV)
            INVENTORY.import_data(data=initial_data)

    # reload the dev server upon HTML changes
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # specify max file upload to be 5MiB
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # run the Flask development server
    app.run(threaded=True, port=5000, use_reloader=True)
