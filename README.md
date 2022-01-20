# Inventory Management System
Shopify 2022 Summer Internship Technical Challenge

> **TASK:** Build an inventory tracking web application for a logistics company. We are looking for a web application that meets the requirements listed below, along with one additional feature, with the options
also listed below.

## Features
* Basic CRUD functionality:
  * Create inventory items: either via the `Add product` button, or by `Import from CSV`
  * Edit product name and quantity
  * Delete products: via `Delete selected` button
  * View products on a web page
* Additional feature:
  * One-button CSV export of product data: via `Export all as CSV`

Developed using Python, SQLite database, Flask, HTML, CSS, JavaScript, and displays a web-based user interface.


## Screenshot
![Main UI Screenshot](https://user-images.githubusercontent.com/10665890/150293250-78c77bd8-1528-48a3-ab8b-adeb2d3e990b.png)


## Prerequisites

### Python
Please use Python version `3.9`. Download and install Python3.9 from the official website: https://www.python.org/downloads/

Ensure you are able to access python from the command-line, verify by executing:
```bash
python3.9 --version
```
Should return the correct Python version number.

### Packages
The following Python packages are used for this project:
```
Flask==2.0.2
Jinja2==3.0.3
mypy==0.931
mypy-extensions==0.4.3
types-Flask==1.1.6
types-Jinja2==2.11.9
types-Werkzeug==1.0.9
typing_extensions==4.0.1
Werkzeug==2.0.2
```
They are also found in [requirements.txt](https://github.com/sammdu/Shopify-Challenge-2022/blob/main/requirements.txt).


## Setup Instructions

### 1. Create a Python virtual environment
```bash
python3.9 -m venv shopify_env_2022
```
Enter the newly created Python virtual environment folder:
```bash
cd shopify_env_2022
```

### 2. Setup the project environment
Clone the project repository from GitHub:
```bash
git clone https://github.com/sammdu/Shopify-Challenge-2022.git
```
Enter the project repository folder:
```bash
cd Shopify-Challenge-2022
```
Activate the Python virtual environment in your terminal:
```bash
source ../bin/activate
```
> After the previous step, you should see the following prompt prepended to your command prompt: `(shopify_env_2022)`, which should be consistent with the Python virtual environment folder name.

Install required Python packages with `pip`:
```bash
pip install -r requirements.txt
```

## Seeing the project in action!
Within an activated virtual environment in the project repository, simply execute the following command to start a Flask development server:
```bash
python3.9 ./main.py
```
This will start a server at [http://127.0.0.1:5000/](http://127.0.0.1:5000/). Visit this address in your browser to see the project in action!


## Testing
### 1. Type verification with `mypy`
In the project repository root, where the `mypy.ini` file is located, simply execute the following command to test for type violations:
```bash
mypy
```
