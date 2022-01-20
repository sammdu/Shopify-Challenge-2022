// URL root path of the current page
const page_url_root = window.location.protocol + '//' + window.location.host;

// list of product SKUs that are selected
let selected_products = new Set();


/*
    Function that gets called upon every page load.
*/
function onPageLoad() {
    // add all checked products to the set of selected products
    let checkboxElems = document.getElementsByName("select-item");
    for (let checkbox of checkboxElems) {
        if (checkbox.checked === true) {
            let sku = rowIdToSKU(checkbox.parentNode.parentNode.id);
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
        let link = page_url_root + '/export-csv?items=' + JSON.stringify(selected);
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
        const file = document.getElementById('importCsvElem').files[0];
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
    Add a new product row at the top of the table and disable the "Add product" button
*/
function addProduct() {
    // clone the new product row template and make it visible
    const newProductTmpl = document.getElementById('newProductTmpl');
    const newProductRow = newProductTmpl.cloneNode(true);
    newProductRow.id = 'newProductActive';
    newProductRow.style.display = 'table-row';
    newProductTmpl.parentNode.insertBefore(newProductRow, newProductTmpl.nextSibling);

    // disable the add product button: only add one product at a time
    setAddProductButton(false);
}


/*
    Triggered by the `save` button in a new product row. Submits the new product
    information to be inserted into the products inventory.
*/
async function submitNewProduct() {
    // collect data from the active
    let data = {
        'sku': document.querySelector('#newProductActive input[name="product-sku-new"]').value,
        'name': document.querySelector('#newProductActive input[name="product-name-new"]').value,
        'quantity': document.querySelector('#newProductActive input[name="quantity"]').value,
    };

    // POST request payload with necessary information for new product addition
    const payload = {
        method: 'POST',
        headers: {'Content-Type': 'application/json;charset=UTF-8'},
        body: JSON.stringify(data, null, 4)
    };

    try {
        const response = await fetch(page_url_root + '/add-product', payload);

        // if successfully added a new product
        if (response.status === 200) {
            await refreshInventory();   // refresh the inventory
            selectAllProducts(false);   // deselect all products
            setAddProductButton(true);  // enable the add product button
        }
        else {
            throw response.status;
        }
    }
    catch(e) {
        alert("Adding new product failed. See console for details.");
        console.log(data);
        console.log(e);
    }

    // toggle buttons that only work when at least one product is selected
    setSelectOnlyButtons();
}


/*
    Delete the products specified in the `selected` list parameter.
    Calls /delete-products, and asks the user to confirm before proceeding.
*/
async function deleteProducts(selected) {
    // ask user to confirm before proceeding
    const message = 'Are you sure you want to delete the selected products?\n' +
        'This action cannot be undone.';
    let confimation = window.confirm(message);

    if (confimation === true) {
        try {
            const response = await fetch(
                page_url_root + '/delete-products?items=' + JSON.stringify(selected),
                {method: 'DELETE'}
            );

            // if request was successful, refresh the inventory and deselect all products
            if (response.status === 200) {
                await refreshInventory();
                selectAllProducts(false);
            }
            else {
                throw response.status;
            }
        }
        catch(e) {
            alert("Deleting selected products failed. See console for details.");
            console.log(e);
        }
    }
}


/*
    Rename the product which triggered this function in the products inventory.
*/
async function renameProduct(event) {
    let nameElem = event.target;

    // switch the product name cell's state back to show after edit is complete
    productNameSwitchState(nameElem.parentNode, 'show');

    // get new name from the input and set the span content to its value
    let new_name;
    for (let elem of nameElem.parentNode.children) {
        if (elem.nodeName === 'INPUT' && elem.name === 'product-name') {
            new_name = elem.value;
        }
    }
    for (let elem of nameElem.parentNode.children) {
        if (elem.nodeName === 'SPAN' && elem.className === 'product-name') {
            elem.textContent = new_name;
        }
    }

    // POST request payload with necessary information for name change
    const payload = {
        method: 'POST',
        headers: {'Content-Type': 'application/json;charset=UTF-8'},
        body: JSON.stringify({
                'sku': rowIdToSKU(nameElem.parentNode.parentNode.id),
                'new_name': new_name
            },
        null, 4)
    };

    try {
        const response = await fetch(page_url_root + '/change-name', payload);

        // if request was successful, refresh the inventory
        if (response.status === 200) {
            await refreshInventory();
        }
        else {
            throw response.status;
        }
    }
    catch(e) {
        alert("Renaming product failed. See console for details.");
        console.log(data);
        console.log(e);
    }
}


/*
    Switch a product name <td> cell's state between `edit` and `show`.
        - `edit` state is when the <input> element and the save button is shown
        - `show` state is when the <span> element and the edit button is shown
*/
function productNameSwitchState(cell, state) {
    // state can only either be 'edit' or 'show'
    console.assert(state === 'edit' || state === 'show', 'invalid product name state');

    let curr_name;
    for (let elem of cell.children) {
        // swap span and input elements
        if (elem.nodeName === 'SPAN' && elem.className === 'product-name') {
            elem.style.display = (state === 'edit' ? 'none' : 'inline');
            curr_name = elem.textContent;
        }
        else if (elem.nodeName === 'INPUT' && elem.name === 'product-name') {
            elem.style.display = (state === 'edit' ? 'inline' : 'none');
            // when switching to edit mode, make input's value the span's value, then
            // focus on it
            if (state === 'edit') {
                elem.value = curr_name;
                elem.focus();
            }
        }

        // swap edit and save buttons
        else if (elem.name === 'edit-name') {
            elem.style.display = (state === 'edit' ? 'none' : 'inline-flex');
        }
        else if (elem.name === 'save-name') {
            elem.style.display = (state === 'edit' ? 'inline-flex' : 'none');
        }
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
            let container = document.getElementById('inventoryContainer');
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
    let checkboxElems = document.getElementsByName("select-item");
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
    let checkbox = event.target;
    // <tr>'s ID is sliced at 4 because its format is `row-<sku>`
    let sku = rowIdToSKU(checkbox.parentNode.parentNode.id);
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
    selecetd. Specifically, "Delete selected" and "Export selected" buttons.
*/
function setSelectOnlyButtons() {
    let spanElem = document.querySelector('span.selected-ops');
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


/*
    Enable/Disable the "Add product" button.
*/
function setAddProductButton(value) {
    let button = document.querySelector('button[name="add-product"]');
    button.disabled = (value ? false : true);
    button.className = (value ? 'btn-green' : 'btn-disabled');
}


/* Helper function that converts an inventory table's row ID to the product SKU. */
function rowIdToSKU(rowId) {
    return rowId.slice(4);
}


onPageLoad();
