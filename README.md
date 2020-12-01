# Goal
We want to create a tool which allows Boston officials to know which RTA stops would
provide the most benefit to the public with respect to government income if the 
stop was removed.

We plan on doing this by ranking bus stops by the area's average income level, 
and the amount of revenue a bus stop generates.

# Code 
Can be found in the python notebooks under the src folder.

# Datasets
Can be generated by running the code under the transit-equity folder.

Labels/features of each generated file:

## rta_bus_ridership_ma.csv
Caontains ridership data for every RTA in MA. Original data source can be found [here](https://www.transit.dot.gov/sites/fta.dot.gov/files/2020-10/August%202020%20Adjusted%20Database.xlsx).
1. 5 digit NTD ID - The Transit Property’s NTD identification number in the Next Generation NTD Database.
2. Agency - Name of the RTA.
3. Service Area Property - The population of the area served by the property, as reported by the transit property.
4. Active - Indicates whether a property reports (active) or not (inactive) during the most recent Annual report year.
5. Passenger Miles FY - Total number of miles traveled by all passengers forthe most recent closed-out annual report year.
6. Unlinked Passenger Trips FY - Total number of boarding passengers for the most recent closed-out annual report year. 
7. Fares FY - The fare revenues collected during the most recent closed-out annual report year.
8. Operating Expenses FY - Total cost for operating this RTA for the most recent closed-out annual report year.
9. Average Cost per Trip FY - The ratio of Total Operating Expenses per Unlinked Passenger Trips
10. Average Fares per Trip FY - The ratio of Fares Earned per Unlinked Passenger Trips.

## rta_bus_route_ma.csv
Contains all RTA bus routes in MA. Original data source can be found [here](https://hub.arcgis.com/datasets/MassDOT::rta-bus-routes?selectedAttribute=continuous_drop_off).
1. OBJECTID - Id of the route as an object from the datasource. 
2. shape_id - Id of the route geometry shape.
3. agency_id - Id of the agency which corresponds to each RTA.
4. route_id - Id of each bus route.
5. route_short_name - The name (i.e. route 11) of the bus route.
6. route_long_name - A more descriptive name of the bus route (i.e. VA Hospital via Belmont).
8. route_url - Url with more information on the bus route.
9. Angecy - Name of RTA that the route belongs to.
10. ShapeSTLength - Length of the bus route geomtry line.

## rta_bus_stop_income_ma.csv
Contains all RTA bus stops with the census tract that it is part of and the correspoding census tract median household income. Original data source for bus stops can be found [here](https://hub.arcgis.com/datasets/MassDOT::rta-bus-stops) and census income data [here](https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:*&in=state:25).
1. geometry - Geometry point (containing the latitude and longitude) of the bus stop.
2. OBJECTID - Id of the bus stop as an object from the datasource. 
3. stop_id - Id of each bus stop.
4. stop_name - Descriptive name of the bus stop (i.e. Belair St at Colonel Bell Drive).
5. stop_lat - Bus stop latitude, which is extracted from the geometry column for easier access.
6. stop_lon - Bus stop longitude, which is extracted from the geometry column for easier access.
7. stop_url - Url with more information on the bus stop.
8. Agency - Name of the RTA that the stop belongs to.
9. census_tract - The census tract that the bus stop is in.
10. median_household_income - Median household income for the census tract that the bus stop is in.
11. county - The county number that the bus stop is in.
12. population - The population of the county that the bus stop is in.

## bus_stop_route_mapping.csv
Contains a mapping for each RTA bus stop to a RTA bus route. This is needed as an intermediate step to join the bus stops, routes, and income together. No new attributes are introduced in this file. 

## result.csv
The result of joining all datasets together. This csv file contains RTA bus stops, corresponding bus routes, income, and population. No new attributes are introduced in this file. We use this file for creating Tableau visualizations and analyzing the strategic questions.

# Tableau Visualizations
Can be found [here](https://public.tableau.com/views/final_16067610536060/Dashboard1?:language=en&:display_count=y&publish=yes&:origin=viz_share_link).

# Strategic Questions
1. What bus routes and stops, if made free, would most benefit low income riders in Massachusetts?

2. Which towns and districts would most benefit by a policy change to the fare change to these routes?

3. What would the cost be to the MBTA and regional transit authorities for each proposed bus route/stop/zones based on ridership and fare costs?

4. What would the cost be to make an entire regional transit area free and how would this compare?
