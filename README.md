# BLS_metro
This is the reconstruction of works I did at the end of 2018 as a final-term project to analyze and predict (naively)
 which metro region is the best in terms of price inflations and wage levels.
 
Despite the change in the analytical tool, main proceducre is similar.

## Basic idea
* Which areas will be better off when it comes to wage increases compared to 2010 and number of **Finance** job opportunities? (This is because I was studying Finance at the time)
* Which area is less expensive in terms of inflations (Consumer Price Index, specifically) ?

## Basic procedures
* Weed out regions which doesn't have enough job opportunities (less than mean value of total areas)
* Calculate percent changes from 2010 (While CPI itself is relative measures, for this purpose, it should be recalculated as well)
* Construct three different scenarios reflecting different emphases and calculate CPI score based on selected items only 
* Finally, divide wage increases by this CPI score

## Assessment Criteria
Criteria is pretty simple. It was to figure out which areas have larger than 100% (wage increases can cover price changes). This is admittedly pretty naive assessment category, but it gave me some ideas about regions in the US economic situations.

## Future developments
After the reconsruction process for 2019 data is completed, Dashboard for interactive controls is likely to be followed.
Basic machine learning method is to be implemented likewise.
