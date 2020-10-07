# Approach
## Step One:
Create a spreadsheet of all the different bus stops in Massachusetts including MBTA, Regional Transit Authorities, and City/Town buses.

[RTA Bus Stops](https://geo-massdot.opendata.arcgis.com/datasets/rta-bus-stops/data)

[MBTA Bus Stops](https://docs.digital.mass.gov/dataset/massgis-data-mbta-rapid-transit)

## Step Two:
Assign an [income level](https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:*&in=state:25) to each stop based on the census tract data

Perhaps we can use insurance API's to find income levels.

We need to map the above income level census data to areas

## Step Three:
Determine average fare for each transit stop based on fares for 

[MBTA Fare Calculator](https://www.mbta.com/fares)

[RTA Fares](https://www.mass.gov/info-details/public-transportation-in-massachusetts#map-of-transit-authorities-in-massachusetts-)

## Step Four:
Calculate bus [ridership](https://mbta-massdot.opendata.arcgis.com/datasets/mbta-bus-ridership-by-trip-season-route-line-and-stop) for each transit authority.

## Step Five:
Identify which bus routes, stops, or zones would have the most positive effect on low income riders if free. Identify which towns would be impacted?

Rank stops based on income level weighed by traffic to allow 

## Step Six:
Generate visualizations: TBD with client using software such as ArcGIS or tableau as a final deliverable along with the list data.


## Additional Metrics
Using [walk scores](https://www.walkscore.com/professional/public-transit-api.php#route) to figure out routes if needed