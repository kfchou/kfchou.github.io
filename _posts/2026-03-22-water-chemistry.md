---
layout: post
title:  "Coffee Water Composition"
categories: [Coffee]
---

TL;DR: Boston's tap water is terrible for making high quality coffee (wrt aroma and taste). No need to start at zero with deionized water -- spike your water to get better results. In these notes, I aim to derive a recipe for optimizing my flat whites using Boston's (filtered) tap water.

## Introduction
Coca Cola famously re-mineralizes distilled water in their plants across the world, to ensure their products have a consistent flavor throughout the world.

It's the same for coffee. The chemistry behind water is complex, and still not fully understood. Colonna-Dashwood & Hendon's [Water for Coffee](https://www.amazon.ca/Water-Coffee-Science-Story-Manual/dp/1782806083) (2015) takes a deep dive into this topic. To make this more approachable, [Third Wave Water](https://thirdwavewater.com/) has built a whole business to help you achieve a desired mineral composition specifically for various types of coffee -- simply add their mineral packs to distilled water.

Various recipes will talk about adjusting the total hardness (ppm $$CaCO_3$$) and alkalinity (ppm $$CaCO_3$$) by focusing on the content of calcium and magnesium. The [Coffee ad Astra Blog](https://coffeeadastra.com/2018/12/16/water-for-coffee-extraction/) summarized this well into a beautiful figure:

![GH vs KH](/assets/2026-03-22/water-chemistry.png)

Figure 1: Total Hardness vs Alkalinity: Target values, by Coffee ad Astra. Grey boxes describe the coffee brewed with water hardness and alkalinity in that region. See "Chemistry Overview" for an explanation of "Total Hardness" and "Alkalinity".
{: .post-subheading }

Several interesting takeaways:
* Boston's tap water produces weak, sour, and sharp coffee (bottom left)
* "Most naturally occurring water will fall near [the 1:1 line] because of how water acquires its minerals by dissolving limestone."
* Third Wave Water (TWW) classic and espresso profiles achieves a relative hard profile

The circled regions indicate the ranges recommended by:
* The Specialty Coffee Association SCA (green bar)
* Colonna-Dashwood & Hendon (2015) [Water for Coffee](https://www.amazon.ca/Water-Coffee-Science-Story-Manual/dp/1782806083) book
* Specialty Coffee Association of Europe (SCAE)

To "fix" the water issue, we need to adjust our water composition to be within these regions.

## Brief Chemistry Overview
Total hardness in Figure 1 is synonymous with General Hardness (GH), which measures the amount of dissolved calcium ($$Ca^{2+}$$) and magnesium ($$Mg^{2+}$$) ions. These ions help pull out aromatic compounds during the extraction process.
* Magnesium is more "aggressive" at pulling out organic acids and fruity esters
* Calcium help extract heavy oils and tactile components
* A higher GH helps with extracting more flavor out of the coffee
* If GH is too high, you can over-extract the coffee, hence there are specific recommendations of GH level for different roast levels.

Alkalinity and Carbonate Hardness (KH) are synonymous in this context. While Alkalinity measures all buffers (borates, phosphates, etc), city water's alkalinity comes mostly from bicarbonates. KH acts as a buffer:
* If KH is too high, it will soak up the bright, aromatic acids, resulting in a flat, dull cup.
* If KH is too low, the high acidity from coffee will taste metallic or sour.

## Recipes
You can find many recipes referenced in the figure above in the [Coffee ad Astra Blog](https://coffeeadastra.com/2018/12/16/water-for-coffee-extraction/). But I don't want to go through the hassle of buying distilled water. Mineral packs present an additional cost. Furthermore, many sources that talk about coffee water focuses on calcium and magnesium. Natural mineral waters ought to have other minerals in them that affect the taste of coffee.

> There's a certain "edginess" and "emptiness" to remineralised distilled water when compared to suitable "natural" water.
> 
> I think what [Colonna-Dashwood & Hendon] have found also speaks to why some mineral waters or heavily bypassed tap waters brew amazing coffee even though they might not, on paper, seem ideal ([u/ego_brews](https://www.reddit.com/r/pourover/comments/1bemk3z/water_for_coffee_2_book_due_later_in_the_year/))


**My goal here is to find a recipe to spike the soft boston tap water** (post-filtering) to achieve a mineral composition that is more suitable for aroma-maxxing my espresso shots.

### Target GH and KH Ratios
Flat whites are my preferred drink, and I need to make sure the flavor of the milk doesn't overwhelm the delicate flavors of the coffee. Therefore, the **GH needs to be high** (>50 ppm) for a more intense extraction. Additionally, higher amount of magnesium will help with the extraction of the bright acids.

Milk is slightly acidic, but it is a power buffer. The proteins act as chemical "sponges" that can absorb hydrogen ions from the coffee's acids. Additionally, the phosphate ions in milk are classic buffering agents in chemistry. Adding an espresso (pH ~4.5) into milk will neutralize the flavorful aromatic compounds.

To overcome the effects of milk, we **increase the water's KH** to form organic acid salts in the espresso. These compounds are more stable, and it's more difficult for milk to neutralize the aromatics in this form. We aim to increase the water's KH to **50-60 ppm**.

The Book *Water for Coffee* [recommends](https://water.viomi.com/blogs/hydration-lab/water-quality-for-coffee-brewing-guide#:~:text=For%20espresso%2C%20many%20aim%20somewhat%20higher%2C%20often,Calcium%20and%20Magnesium%20For%20Body%20And%20Sweetness.) aiming for a GH:KH ratio of 2:1, so let's aim for a GH of **~80-100ppm**.

### Adjusting GH and KH ratios
Barista Hustle provides a [calculator](https://www.baristahustle.com/app-archive-main/the-water-calculator/) to combine premixed "Hard" and "Buffer" solutions, to which you add to your water to achieve your desired mineral composition.

First, prep these two solutions:
* Hardness Solution: 2.45 g of Epsom salts ($$MgSO_4$$) in 1L of water
* Buffer Solution: 1.68 g of sodium bicarbonate in 1L of water

Then, assuming Boston tap water has these properties ([source](https://www.home-barista.com/water/boston-water-and-options-t72187.html)):

| Metric | Boston Tap Water |
|---|---|
| Total Dissolved Solids (TDS) | 107 ppm |
| pH | 9–9.5 |
| General Hardness (GH) | 35–53 ppm, 15–36 ppm (unverified for Ca specific hardness) |
| Carbonate Hardness (KH) | 53–71 ppm, 30–54 ppm |

note: 
* Different value ranges are given, depending on the source (random forums).
* Both GH and KH are usually measured in calcium carbonate equivalents. It’s measured this way because simple drop test kits can’t distinguish between calcium or magnesium ions, so it’s easiest to assume it’s all calcium.

Next, we determine your target range of GH and KH values.  I'm aiming for GH 80ppm and KH 50ppm

Plug the GH and KH values into the calculator to get:

| Solution | Figure 1 | Source 1 | Source 2 |
|---|---|---|---|
|Hardness (g) | 60 | 45 | 45 |
|Buffer (g)| 34 | 15 | 0 |
|Water (g)| 906| 940 | 955 |

Due to the discrepancy of GH and KH values from different sources, it's better to use an actual GH/KH drop test kit to test the hardness of your water.

Note: I'll make edits here as I collect more data
---

By adjusting ratio of the three components and target values, you get various recommended recipes from the Coffee ad Astra figure above. Assuming starting with deionized (DI) water:

| Recipe | Buffer | Hardness | Water | Notes |
|---|---|---|---|---|
| Melbourne | 11.5g | 23.7g | 964.8g  | City Water Approx |
| WOC Budapest | 40.1 | 51.2 | 908.7 |  - |
| SCA | 40.1 | 68.6 | 891.3 | SCAA 2009 Handbook |
| [Rao](http://www.scottrao.com/) | 50.1 | 75.7 | 874.2 | - |
| Hendon | 30.8 | 99.9 | 869.3 | Author of [Water for Coffee](http://waterforcoffeebook.com/) |
| Barista Hustle | 80.1 | 80.7 | 879.2 | - |
| Pretty Hard | 35.1 | 126.1 | 838.9 | - |
| Hard AF | 45.2 | 176.8 | 778 | - |

Note: all recipes from the [Barista Hustle blog](https://www.baristahustle.com/diy-water-recipes-redux/)


### Incorporating Other Minerals
Coffee ad Astra takes it [a step further](https://coffeeadastra.com/2019/08/23/a-tool-and-videos-for-crafting-custom-brew-water/) with their own [calculator](https://docs.google.com/spreadsheets/d/1SRY9sn1NiWYfOms7knH__j_Iw-OwW6vU2JpWjA4P3jY/edit?gid=1238625780#gid=1238625780) by also taking into account of sulfate and sodium ions. The ingredients involved are:

* Epsom Salt (MgSO4•7H2O)
* Magnesium Chloride Hexahydrate (MgCl2•6H2O)
* Calcium Chloride anhydrous (CaCl2)
* Baking Soda (NaHCO3)
* Potassium Bicarbonate (KHCO3)

If you only have access to a subset of these ingredients, alternative calculators can be found in different pages of the spreadsheet.

This calculator provides a single concentrate, as opposed to a two-concentrate solution like Barista Hustle.

Disclaimer: I haven't tried this calculator.

## Further Readings
[Understanding Water Quality for Brewing Championship Coffee](https://water.viomi.com/blogs/hydration-lab/water-quality-for-coffee-brewing-guide#:~:text=For%20espresso%2C%20many%20aim%20somewhat%20higher%2C%20often,Calcium%20and%20Magnesium%20For%20Body%20And%20Sweetness.) - Viomi