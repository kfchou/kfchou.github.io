---
layout: post
title:  Boston Shoreline Over Time
categories: [Visualization]
---
A look at how the shoreline of Boston changed over time, which partially explains why the streets of Boston is so poorly laid out.

<style>
.content-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
}
.image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 80%;
    height: 70%;
    background-color: #fff;
    position: relative;
}
#background-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}
#displayed-image {
    position: relative;
    max-width: 100%;
    max-height: 100%;
    z-index: 2;
}
.slider-container {
    width: 80%;
    margin-top: 20px;
    position: relative;
}

#image-slider {
    width: 100%;
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    top: 25px;  /* Adjust this value to fine-tune the vertical alignment */
    width: 100%;
}

.slider-labels span {
    text-align: center;
    position: relative;
}
</style>

<script src="{{ site.baseurl }}/assets/2024-07-13-boston-map/script.js"></script>


<div class="content-container">
    <div class="slider-container">
        <div class="slider-labels">
            <span id="label-0">1630</span>
            <span id="label-1">1795</span>
            <span id="label-2">1852</span>
            <span id="label-3">1880</span>
            <span id="label-4">1916</span>
            <span id="label-5">1934</span>
            <span id="label-6">1950</span>
        </div>
        <input type="range" id="image-slider" min="0" max="6" value="0">
    </div>
    <div class="image-container">
        <img id="background-image" src="{{ site.baseurl }}/assets/2024-07-13-boston-map/boston_2024.png" alt="Background Image">
        <img id="displayed-image" src="{{ site.baseurl }}/assets/2024-07-13-boston-map/boston_1630.png" alt="Image">
    </div>
</div>

### Credits
Inspired by [Daniel Steiner](https://www.youtube.com/watch?v=UA63zaIXCZw)'s video on Boston.

Cartography by Herb Heidt and Eliza McClennen of MapWorks for Mapping Boston edited by Alex Krieger and David Cobb with Amy Turner. Cambridge, MA : MIT Press, 1999. Accessed via the [Levanthal Map Collections](https://collections.leventhalmap.org/search/commonwealth:q524n4440).