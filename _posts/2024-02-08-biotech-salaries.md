---
layout: post
title:  r/biotech Salary Survey
categories: [salaries, visualizations]
---

What are the normal salary ranges in biotech? How does this change for different experience levels? How much do bonuses and equities contribute to income? In this post, we explore these questions and more using survey data from r/biotech.

## Base Salary Ranges
The 2023 survey had 670 responses, of which 611 are from the U.S. Non-U.S. responses are excluded because the compensation range tends to differ drastically between the U.S. and other countries. Though there are more nuances based on economic regions within the U.S. (e.g., large coastal cities vs Mid-West or Southern cities), I won't dive into that here.

After some extensive data cleaning, I grouped each response into approximate seniority levels based on their reported job title (see "methodologies" below). The figure below shows the base compensation distributions for different seniority levels as boxenplots.

There are a lot of overlaps across different seniority levels, but this is to be expected. Companies of different sizes, job track, and job type all have salary bands that are not standardized.
<br>
<br>

![Biotech Salaries; base vs equity, U.S.](/assets/2024-02-08-biotech/base-range.png)

Side note: Boxenplots combine boxplots with histograms. It divides the data into quantiles. The width of each box represents proportionally the amount of data in that quantile. This kind of representation allows us to better visualize  the shape of distribution, especially at the tails.

## Contribution of Non-Base Compensations
Out of the survey respondants, 25% don't have annual bonuses
and 69% don't have annual equities. But, out of those who do have annual bonuses and equities, these incentives contribute to a significant amount to the respondants' total compensation. The figure below shows the median annual base, bonus, and equity of respondents, excluding responses with no bonuses and equities.
<br>
<br>

![Biotech Salaries; base vs equity, U.S.](/assets/2024-02-08-biotech/base-vs-equity.png)

During salary negotiations, there may be more wiggle room with these other sources of income than the base compensation.

## Base Salary by Company Size
Some people ask to have "manager" or "lead" in their job title, since these words usually carry a degree of prestige. It's easier to obtain these titles at smaller companies, so these titles carry less weight depending where a person works.
<br>

![Biotech Salaries by company size, U.S.](/assets/2024-02-08-biotech/base-vs-size.png)


### Methodology
Job titles are grouped into seniority based on typical science-track hierarchies:

* Technicians: Lab technician or any title with "technician".
* Associates: Research assistants and research associates are grouped together, although associates can considered a higher level than assistants.
* Scientist: Include biologists and microbiologists.
* Manager: Includes project managers, research or scientific managers, and managers of various functions with explicit "manager" titles.
* Lead/Principal/Staff/Director: "Lead" and "director" are usually management track, while "principal" and "staff" are individual contributor track. These positions are grouped together since "principal" and "director" are often considered the same level, and elsewhere, "lead" is considered the same level as "principal", and "staff" can be considered the same level as "director". The terminology is not standardized across the indistry.
* VP or higher: Includes all exec-level positions, for example, "heads" of departments and c-suite levels.
