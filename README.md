# BLS_metro
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/staedi/bls_metro/app.py)

This is the reconstruction of works I did at the end of 2018 as a final-term project to analyze and predict (naively)
 which metro region is the best in terms of price inflations and wage levels.
 
The analysis framework has recently been incorporated into web application with `Streamlit`, which is accesible via [Streamlit sharing](https://share.streamlit.io/staedi/bls_metro/app.py). 

## Data sources
US Bureau of Labor Statistics
* [State and Metro Area Employment, Hours & Earnings](https://www.bls.gov/sae/)
* [Consumer Price Index - All Urban Wage earners and clerical workers (CPI-W)](https://www.bls.gov/cpi/data.htm)

US Census Bureau
* [Cartographic Boundary Files - Shapefile](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html)

## Dashboard developments

### Selectible Options
* Employment Sectors: Supersector where employment is collected (e.g., *Financial Activities*)
* Target year: Year to analyze the figures (**employment strengths** and **price indexes**) based on the year *2010*
* Limits: Number of top metro areas to be selected upon employment strengths
* Scenario: Spending category based on Consumer Price Index summary data

### Features
* Scatter chart: Laying out relations between Employees numbers and Workers' average hourly earnings
* Stacked bar chart: Disect items of price index (Weight values are applied on the graph)
* Bar chart: Compare pricing power of metro-areas (calculated with **wages increases** over **price increases** for the given timeframes)
* Choropleth: Show each metro-area on US maps with calculated information 
 * Color depths: *Blue* to *Red* according to **Pricing Power** (neutral means border-line)
 * Elevations: **Employment strengths**

## Basic idea

### Motivations
* Which areas will be better off when it comes to wage increases compared to 2010 and number of **Finance** job opportunities? (This is because I was studying Finance at the time)
* Which area is less expensive in terms of inflations (Consumer Price Index, specifically) ?

### Basic procedures
* Weed out regions which doesn't have enough job opportunities (less than mean value of total areas)
* Calculate percent changes from 2010 (While CPI itself is relative measures, for this purpose, it should be recalculated as well)
* Construct three different scenarios reflecting different emphases and calculate CPI score based on selected items only 
* Finally, divide wage increases by this CPI score

### Assessment Criteria
Criteria is pretty simple. It was to figure out which areas have larger than 100% (wage increases can cover price changes). This is admittedly pretty naive assessment category, but it gave me some ideas about regions in the US economic situations.
