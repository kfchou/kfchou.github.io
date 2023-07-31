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

<div>
<iframe src="/assets/best_dishes_bos23_bar.html" height="500" width="1000" class="chart"></iframe>
</div>

<div>
Hover over a circle to see the dish, restaurant, and number of votes!
<iframe src="/assets/best_dishes_boston_2023.html" height="500" width="1000" class="chart"></iframe>
</div>

## Methodology
In liu of using reddit's API, I copied the entire HTML from [this reddit thread](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/) and parsed it with [BeautifulSoup](https://github.com/wention/BeautifulSoup4).
After some manual cleaning, I used plotly and folium to visualize the most-upvoted dishes from the thread. Irrelevent responses (e.g., water) were removed from the dataset.

### Map upvotes to a color hex
```py
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

norm = mcolors.Normalize(vmin=10, vmax=500, clip=True)
mapper = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.plasma)
df['color_hex'] = df['votes'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))
```


### Barchart
```py
df_partial = df[~pd.isna(df['latitude'])].iloc[:50]
fig = go.Figure(go.Bar(
            x=df['votes'],
            y=df['dishes'].str.strip()+', '+df['yelp name'],
            orientation='h',
            marker=dict(
                color=df['color_hex'],
            )
        ))

maintitle = "r/Boston's favorite dishes, 2023"
subtitle = "<br><span style='font-size: 12px;'>Double click to zoom out</span>"
fig.update_layout(
    title=f"{maintitle}{subtitle}",
    xaxis_title='# Upvotes',
    yaxis_title='Dish, Restaurant',
    yaxis=dict(
        range=[10.5,-0.5] # initial zoom setting
        ),
)

fig.show()

fig.write_html("../data/best_dishes_bos23_bar.html") # export figure as html
```

Map:
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
        folium.Circle(location=location,
                        # popup = r['total_value'],
                        tooltip=f"{r['dishes']}<br>{r['yelp name']},\n{r['votes']} votes",
                        radius=r['votes']*1.2+50,
                        fill=True,
                        fill_color=r['color_hex'],
                        stroke=False,
                        fillOpacity=0.5
                    ).add_to(m)

# to visualize the map, call `m` in Jupyuter Notebook

# export map as html
m.save("best_dishes_boston.html")

```

## Source
[r/Boston](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/)