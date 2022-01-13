#!/usr/bin/env python3.9
"""

"""

from flask import Flask, render_template, request, make_response, jsonify, session
from csv_utils import csv_to_list

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    """
    return render_template('index.html')


if __name__ == '__main__':
    # run the Flask development server
    app.run(threaded=True, port=5000)
