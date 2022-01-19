#!/usr/bin/env python3.9
"""
Functions that actually perform the substantial tasks in main.py, as well as any helper
functions necessary.
"""

from flask import Response, make_response
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import time

from modules.products import Products
from modules.csv_utils import csv_to_list, sqlite_rows_to_csv


def export_csv(inventory: Products, items_param: str, path: str) -> Response:
    """
    Export the products in `inventory` specified by `items` into a CSV file at `path`.
    If `items` is empty, export all products.
    """

    # try to read the list of items to export from the GET parameter `items`
    try:
        items: list = json.loads(items_param)
        assert isinstance(items, list)
    except Exception as err:
        print(f"---\nEndpoint: /export-csv\n{err}\n---")
        return make_response(
            "Parameter error! Must provide a JSON list of SKU strings for `items`.",
            400
        )

    # get the products specified by items; empty list results in all products being dumped
    dump: list
    if items == []:
        dump = inventory.get_all()
    else:
        dump = inventory.get_specific(skus=items)

    # try to convert the list of SQLite Rows in the dump to a CSV file
    try:
        sqlite_rows_to_csv(dump, path=path)
    except Exception as err:
        print(f"---\nEndpoint: /export-csv\n{err}\n---")
        return make_response(
            "Server could not export the CSV file. Please try again.",
            500
        )

    return make_response("ok", 200)


def _allowed_filetype(filename: str, allowed_exts: set) -> bool:
    """
    Helper function to verify a given `filename` has an extension that's within
    `allowed_exts`.
    """
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in allowed_exts)


def import_csv(inventory: Products, post_file: FileStorage) -> Response:
    """
    Import the products from the uploaded CSV file `post_file` into the `inventory`.
    """
    # check that a file is selected
    if type(post_file.filename) != str or (post_file.filename == ''):
        return make_response("No file selected.", 400)

    # check that the file is non-empty and has a valid extension; then save it temporarily
    if post_file and _allowed_filetype(filename=post_file.filename, allowed_exts={'csv'}):
        # temp filename is `upload_<unix_timestamp>_original_filename.csv`
        saved_filename = ''.join(
            ('./upload_', str(int(time.time())), '_', secure_filename(post_file.filename))
        )
        post_file.save(saved_filename)
    else:
        return make_response(
            "Incorrect file extension (must be CSV), or invalid file.", 400
        )

    # read the temporary CSV file and import the data into the inventory database
    try:
        data_to_import: list[dict] = csv_to_list(saved_filename)
        inventory.import_data(data=data_to_import)
    except Exception as err:
        print(f"---\nEndpoint: /import-csv\n{err}\n---")
        return make_response(
            "Server could not import the CSV file. Please try again.",
            500
        )

    # delete the uploaded CSV file
    Path(saved_filename).unlink()

    return make_response("CSV data imported successfully!", 200)
