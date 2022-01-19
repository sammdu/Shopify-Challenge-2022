// URL root path of the current page
const page_url_root = window.location.protocol + '//' + window.location.host;

// list of product SKUs that are selected
let selected_products = [];

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
    Export the products specified in the global `selected_products` variable as a CSV file.
    Calls /export-csv, and if the list is empty, will return all products.
*/
function exportProducts() {
    try {
        link = page_url_root + '/export-csv?items=' + JSON.stringify(selected_products);
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
