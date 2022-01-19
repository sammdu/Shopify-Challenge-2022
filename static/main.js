// URL root path of the current page
const page_url_root = window.location.protocol + '//' + window.location.host;

// list of product SKUs that are selected
let selected_products = new Set();


/*
    Function that gets called upon every page load.
*/
function onPageLoad() {
    // add all checked products to the set of selected products
    checkboxElems = document.getElementsByName("select-item");
    for (let checkbox of checkboxElems) {
        if (checkbox.checked === true) {
            sku = rowIdToSKU(checkbox.parentNode.parentNode.id);
            selected_products.add(sku);
        }
    }

    // toggle buttons that only work when at least one product is selected
    setSelectOnlyButtons();
}


/*
    Export the products specified in the `selected` list parameter as a CSV file.
    Calls /export-csv, and if the list is empty, will return all products.
*/
function exportProducts(selected) {
    try {
        link = page_url_root + '/export-csv?items=' + JSON.stringify(selected);
        window.open(link, '_self');
    }
    catch(e) {
        console.log(e);
    }
}


/*
    Triggered by onchange() of #importCsvElem; sends the chosen CSV file to /import-csv.
    Alerts on success and failures.
*/
async function importCsv() {
    try {
        file = document.getElementById('importCsvElem').files[0];
        const formData = new FormData();
        formData.append('file', file);

        const data = {
            method: 'POST',
            body: formData
        };
        const response = await fetch(page_url_root + '/import-csv', data);

        // if request was successful, refresh the inventory
        if (response.status === 200) {
            await refreshInventory();
            alert("CSV import complete!");
        }
        else {
            throw response.status;
        }
    }
    catch(e) {
        alert("Importing CSV failed. See console for details.");
        console.log(e);
    }
}


/*
    Calls /get-inventory and replaces the inventory table with the one returned from the
    backend.
*/
async function refreshInventory() {
    try {
        // ask the server for the inventory table
        const response = await fetch(page_url_root + '/get-inventory');

        // if request was successful, replace the inventory table
        if (response.status === 200) {
            container = document.getElementById('inventoryContainer');
            container.innerHTML = await response.text();
        }
        else {
            throw response.status;
        }
    }
    catch(e) {
        console.log(e);
    }
}


/*
    Either select or de-select all products, depending on the boolean parameter `value`.
*/
function selectAllProducts(value) {
    checkboxElems = document.getElementsByName("select-item");
    for (let checkbox of checkboxElems) {
        if (typeof value === 'boolean' && checkbox.checked != value) {
            checkbox.click();
        }
    }
}


/*
    Triggered when a product's checkbox has been checked.
    Includes the product within the set of `selected_products`.
*/
function productSelected(event) {
    checkbox = event.target;
    // <tr>'s ID is sliced at 4 because its format is `row-<sku>`
    sku = rowIdToSKU(checkbox.parentNode.parentNode.id);
    if (checkbox.checked === true) {
        selected_products.add(sku);
    }
    else if (checkbox.checked === false) {
        selected_products.delete(sku);
    }

    // toggle buttons that only work when at least one product is selected
    setSelectOnlyButtons();
}


/*
    Enable/Disable buttons that can only be available when at least one product is
    selecetd. Specifically, "Delete selected" and "Export selected".
*/
function setSelectOnlyButtons() {
    spanElem = document.querySelector('span.selected-ops');
    // enable buttons that only work when at least one product is selected
    if (selected_products.size !== 0) {
        for (let button of spanElem.children) {
            if (button.name === 'del-selected') {
                button.disabled = false;
                button.className = button.className.replace("btn-disabled", "btn-red");
            }
            if (button.name === 'exp-selected') {
                button.disabled = false;
                button.className = button.className.replace("btn-disabled", "btn-purple");
            }
        }
    }
    // disable those buttons otherwise
    else {
        for (let button of spanElem.children) {
            if (button.name === 'del-selected' || button.name === 'exp-selected') {
                button.className = 'btn-disabled';
                button.disabled = true;
            }
        }
    }
}


/* Helper function that converts an inventory table's row ID to the product SKU. */
function rowIdToSKU(rowId) {
    return rowId.slice(4);
}


onPageLoad();
