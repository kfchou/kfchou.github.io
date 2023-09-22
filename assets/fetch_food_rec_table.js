// Your API KEY
const API_KEY = "AIzaSyAwEg3jNDMdedb4v6HAwEKwHON2dtMtIbI";

// Function to fetch data from Google Sheets
function fetchData() {
    // Spreadsheet ID and range
    const spreadsheetId = "1442-rzE9VLjcUoT80eWfmoxuxG2ZJrOAK4UG_LzO4dA";
    const range = "A:H"; // Replace with your sheet name
    gapi.client.sheets.spreadsheets.values.get({
        spreadsheetId: spreadsheetId,
        range: range,
    }).then(function(response) {
        const values = response.result.values;
        buildTable(values);
    });
}

// Function to build HTML table
function buildTable(data) {
    const table = document.createElement("table");
    const thead = table.createTHead();
    const tbody = table.createTBody();
    // Add classes and IDs to the table
    table.classList.add("table");
    table.classList.add("table-hover");
    table.id = "rec_table";
    // Create table headers
    const headerRow = thead.insertRow();
    data[0].forEach(function(cellData, index) {
        const th = document.createElement("th");
        if(index === data[0].length - 1) th.classList.add('notes-column');
        th.textContent = cellData;
        headerRow.appendChild(th);
    });
    // Create table rows with data
    for (let i = 1; i < data.length; i++) {
        const row = tbody.insertRow();
        for (let j = 0; j < data[0].length; j++) {
            const cell = row.insertCell();
            if (j === data[0].length - 1) cell.classList.add('notes-column');
            cell.textContent = data[i][j] || 'n/a';
        }
        // Create tooltip
        if(data[i][data[0].length - 1]) {
            const tooltip = document.createElement("div");
            tooltip.classList.add("custom-tooltip");
            tooltip.textContent = data[i][data[0].length - 1];

            row.addEventListener("mouseover", function(e) {
                tooltip.style.left = e.pageX + "px";
                tooltip.style.top = e.pageY + "px";
                document.body.appendChild(tooltip);
            });

            row.addEventListener("mouseout", function() {
                document.body.removeChild(tooltip);
            });
        }
    }
    // Append the table to a container element
    const tableContainer = document.getElementById("table-container");
    tableContainer.appendChild(table);
    // Initialize DataTables on the table to make it sortable
    $(table).DataTable(
        {"order": [[1, "desc"]],
        "pageLength": 25,
        "lengthMenu": [[10, 25, 50, 100, 200, -1], [10, 25, 50, 100, 200, "All"]],
        }
    );
}
// Initialize Google API client
window.initClient = () => {
    gapi.client.init({
        apiKey: API_KEY,
        discoveryDocs: ["https://sheets.googleapis.com/$discovery/rest?version=v4"],
    }).then(function() {
        fetchData();
    });
}
// Load Google API client
gapi.load("client", initClient);