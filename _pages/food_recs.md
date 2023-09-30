---
layout: page
title: Kenny's Food Recs
permalink: /food-recs/
---

To contribute, please submit your reviews [here](https://docs.google.com/forms/d/e/1FAIpQLSc3rrsBrqAP7WhvTzkQ3CdWUecWeeHMEV7RmaX6Oj8K_jEf5w/viewform?usp=sf_link). The content of this list is updated automatically based on the raw data on [Google Sheets](https://docs.google.com/spreadsheets/d/1442-rzE9VLjcUoT80eWfmoxuxG2ZJrOAK4UG_LzO4dA/edit#gid=0), which is pulled from the survey responses. You can also get more food inspirations on my ig [@kchou.eats](https://www.instagram.com/kchou.eats/).

|**Rating System**:|
| -- |
| 1/5 = Terribad - I regret this decision | 
| 2/5 = Bad - Will not go even if someone else wants to go | 
| 3/5 = Aite - Will go if someone else wants to go  | 
| 4/5 = Great - Would visit again of my own desire  | 
| 5/5 = Wowza - Worth a special trip | 

<br>
All prices are in USD, includes taxes and tips, and excludes drinks.
<br>
<html>
    <head>
        <!-- Include jQuery -->
        <!-- Include DataTables CSS and JS -->
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/3.10.0/mdb.min.css" />
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
        <!-- Google API -->
        <script src='https://apis.google.com/js/api.js'></script>
    </head>
    <style>
        .hidden-column {
            display: none;
        }
        .custom-tooltip {
            position: absolute;
            background-color: #fff;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 4px;
            max-width: 300px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        }
    </style>
    <script src="{{ site.baseurl }}/assets/fetch_food_rec_table.js"></script>
    <script>
        window.initClient(); // Initializes and calls fetchData() and buildTable()
    </script>

<body>
    <div class="table-container" id="table-container"></div>
</body>

</html>

---

You can view the raw-form of the data [here](https://docs.google.com/spreadsheets/d/1442-rzE9VLjcUoT80eWfmoxuxG2ZJrOAK4UG_LzO4dA/edit#gid=0).

Want to contribute your own reviews? Fill out a form [here](https://docs.google.com/forms/d/e/1FAIpQLSc3rrsBrqAP7WhvTzkQ3CdWUecWeeHMEV7RmaX6Oj8K_jEf5w/viewform?usp=sf_link)

Suggestions? Shoot me an [email](kennethfchou@gmail.com).