---
layout: post
title: r/boston's favorite restaurants, 2023.
categories: [Visualizations]
---

<div>
<iframe src="/assets/best_dishes_bos23_bar.html" height="500" width="1000"></iframe>
</div>

<div>
Hover over a circle to see the dish, restaurant, and number of votes!
<iframe src="/assets/best_dishes_boston_2023.html" height="500" width="1000"></iframe>
</div>

## Methodology
In liu of using reddit's API, I copied the entire HTML from [this reddit thread](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/) and parsed it with [BeautifulSoup](https://github.com/wention/BeautifulSoup4).
After some manual cleaning, I used plotly and folium to visualize the most-upvoted dishes from the thread. Irrelevent responses (e.g., water) were removed from the dataset.

## Source
[r/Boston](https://www.reddit.com/r/boston/comments/14jvgf2/single_best_restaurant_menu_item_boston_2023/)