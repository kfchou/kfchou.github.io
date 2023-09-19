---
layout: page
title: Kenny's Food Recs
permalink: /food-recs/
---

This is not a complete list. The content of this list is updated automatically based on the raw data on [Google Sheets](https://docs.google.com/spreadsheets/d/1442-rzE9VLjcUoT80eWfmoxuxG2ZJrOAK4UG_LzO4dA/edit#gid=0). You can also get more food inspirations on my ig [@kchou.eats](https://www.instagram.com/kchou.eats/).

|**Rating System**:|
| -- |
| 1/5 = Terribad - I regret this decision | 
| 2/5 = Bad - Will not go even if someone else wants to go | 
| 3/5 = Aite - Will go if someone else wants to go  | 
| 4/5 = Great - Would visit again of my own desire  | 
| 5/5 = Wowza - Worth a special trip | 

<br>

<html>
<!-- Include jQuery -->
    <!-- Include DataTables CSS and JS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/3.10.0/mdb.min.css" />
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
    <!-- Google API -->
    <script src="https://apis.google.com/js/api.js"></script>
    <script>
        // Your API KEY
        const API_KEY = "AIzaSyAwEg3jNDMdedb4v6HAwEKwHON2dtMtIbI";
        // Function to fetch data from Google Sheets
        function fetchData() {
            // Spreadsheet ID and range
            const spreadsheetId = "1442-rzE9VLjcUoT80eWfmoxuxG2ZJrOAK4UG_LzO4dA";
            const range = "A:G"; // Replace with your sheet name
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
            data[0].forEach(function(cellData) {
                const th = document.createElement("th");
                th.textContent = cellData;
                headerRow.appendChild(th);
            });
            // Create table rows with data
            for (let i = 1; i < data.length; i++) {
                const row = tbody.insertRow();
                data[i].forEach(function(cellData) {
                    const cell = row.insertCell();
                    cell.textContent = cellData;
                });
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
        function initClient() {
            gapi.client.init({
                apiKey: API_KEY,
                discoveryDocs: ["https://sheets.googleapis.com/$discovery/rest?version=v4"],
            }).then(function() {
                fetchData();
            });
        }
        // Load Google API client
        gapi.load("client", initClient);
    </script>
<body>
    <div class="table-container" id="table-container"></div>
</body>
</html>

---

You can view the raw-form of the data [here](https://docs.google.com/spreadsheets/d/1442-rzE9VLjcUoT80eWfmoxuxG2ZJrOAK4UG_LzO4dA/edit#gid=0).

Have restaurants you want to suggest? Shoot me an [email](kennethfchou@gmail.com).