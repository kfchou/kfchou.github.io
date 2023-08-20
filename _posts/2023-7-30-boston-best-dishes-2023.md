---
layout: post
title: r/boston's favorite dishes, 2023.
categories: [Visualizations, Plotly, Folium]
---

<style>
.chart {
    position: relative;
    left: 50%;
    margin-left: -500px;
}
</style>

Users of Reddit [r/Boston](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/) responded to the question "What is the single best restaurant menu item in Boston?" In this post, I compiled their responses and mapped out where you can find those dishes around town. Only top-level responses are considered in the table below. The number of upvotes from repeated responses are added together into a single entry. Responses like "water" are excluded from the dataset.

<div>
<iframe src="/assets/reddit_fav_dishes_Boston_2023_table.html" width="100%" height="600"></iframe>
</div>

<div>
Hover over a circle to see the dish, restaurant, and number of votes!
<iframe src="/assets/best_dishes_boston_2023.html" height="500" width="1000" class="chart"></iframe>
</div>

## Methodology
In liu of using reddit's API, I copied the entire HTML from [this reddit thread](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/) and parsed it with [BeautifulSoup](https://github.com/wention/BeautifulSoup4).
After some manual cleaning, I used plotly and folium to visualize the most-upvoted dishes from the thread. Irrelevent responses (e.g., water) were removed from the dataset. At the end of this process, a dataframe `df` was created with `restaurant`, `dishes`, and `votes`.

Geographical coordinates for each restaurant were the obtained via the Yelp API. The dataframe was additionally populated with columns `yelp name`, `longitude`, and `latitude`.

### Map upvotes to color hex
```py
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

norm = mcolors.Normalize(vmin=10, vmax=500, clip=True)
mapper = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.plasma)
df['color_hex'] = df['votes'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))
```


### Create map marker icons
Folium's defult marker options are circle markers or google-map like icons. Which has a default blue color and isn't customizable.

I want to fill each marker with a color that matches the histogram above. To do this, I first build a customized marker in Adobe Illustrator (you can copy one from the internet, and trace the image to vectorize it). Exporting the SVG and opening it in `notepad` reveals a browser-interpretable SVG code that can be used in conjunction with HTML code.
```xml
<!--Copy and paste this code into a .html file and see what you get-->
<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60.78 96.23">
  <defs>
    <style>
      .cls-1 {
        fill: #a5a5a5;
      }
    </style>
  </defs>
  <g id="Layer_1-2" data-name="Layer 1">
    <path class="cls-1" d="m30.34,96.23c-.74-3.99-1.29-8.03-2.24-11.97-2.97-12.33-8.72-22.98-18.29-31.6C-2.73,41.35-3.26,21.96,8.27,9.62c11.5-12.31,30.67-12.88,42.94-1.27,12.04,11.39,13.06,31.28,1.12,42.74-13.04,12.52-19.17,27.85-21.99,45.15Zm.13-88.07c-12.3-.05-22.26,9.76-22.35,22-.09,12.37,9.99,22.53,22.3,22.5,12.19-.03,22.16-10.03,22.17-22.25.02-12.22-9.92-22.21-22.12-22.26Z"/>
  </g>
</svg>
```

Notice it has a default style with fill color `fill: #a5a5a5`, and the graphic itelf has the class `.cls-1`. I'll modify these properties to assign different fill colors according to each data point's `color_hex` value, as defined earlier.

Unfortunately, I wasn't able to dynamically inject `fill color` properties when calling `folium.Marker()`, so I need to first create a CSS class for each marker color with different `fill` colors, then assign those classes to each corresponding data point using `folium.DivIcon(class_name=my_class_name)`.
```py
# for each color, create an associated css class
class_arr = "."+df['color_hex'].str.replace("#","c-").unique()+" {fill: " + df['color_hex'].unique() + ";}"
marker_class_style = " ".join(class_arr)

# class_arr
# >>> '.c-fdb52e {fill: #fdb52e;}', '.c-ca457a {fill: #ca457a;}' ... etc
```
The modified svg code looks like this:
```py
# svg code
div_icon =f"""
    <svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <defs>
        <style>
        {marker_class_style}
        </style>
    </defs>
    <g id="Layer_1-2" data-name="Layer 1">
        <path d="m30.34,96.23c-.74-3.99-1.29-8.03-2.24-11.97-2.97-12.33-8.72-22.98-18.29-31.6C-2.73,41.35-3.26,21.96,8.27,9.62c11.5-12.31,30.67-12.88,42.94-1.27,12.04,11.39,13.06,31.28,1.12,42.74-13.04,12.52-19.17,27.85-21.99,45.15Zm.13-88.07c-12.3-.05-22.26,9.76-22.35,22-.09,12.37,9.99,22.53,22.3,22.5,12.19-.03,22.16-10.03,22.17-22.25.02-12.22-9.92-22.21-22.12-22.26Z"/>
    </g>
    </svg>
    """
```

### Display data on a map
```py
import folium
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="example app")
# find Boston on the map
boston = geolocator.geocode("Boston")
boston_loc = (boston.latitude, boston.longitude)

# Create a map object and center it to the avarage coordinates to m
m = folium.Map(
    location=boston_loc, 
    zoom_start=13,
    tiles='cartodbpositron')

# add each business object to the map
for i,r in df.iloc[:50].iterrows():
    if (r['latitude'] != 0) & ~pd.isna(r['latitude']):
        location = (r["latitude"], r["longitude"])
        icon_class_name = r['color_hex'].replace("#","c-")
        folium.Marker(
            location=location,
            tooltip=f"{r['yelp name'].title()}:<br>{r['dishes'].capitalize()},\n{r['votes']} votes",
            icon=folium.DivIcon(
                html=div_icon,
                icon_size=30,
                class_name=icon_class_name,
                ),
            popup=f"<div style=\"width: 150px;\">{r['yelp name'].title()}:<br>{r['dishes'].capitalize()}<br>{r['votes']} votes</div>"
            ).add_to(m)

# to visualize the map, call `m` in Jupyuter Notebook

# export map as html
m.save("best_dishes_boston_2023_map.html")

```

## Data Source
[r/Boston](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/)

## Further Reading
* [Using html in Folium](https://towardsdatascience.com/use-html-in-folium-maps-a-comprehensive-guide-for-data-scientists-3af10baf9190)