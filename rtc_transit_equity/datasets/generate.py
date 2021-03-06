import requests
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import json
import geopandas as gpd
import os
import zipfile
from rtc_transit_equity.datasets.lib import get_population, bus_stops_median_household_income, get_median_hh_income, add_census_tract
import time

stops2ridership = {
    'VineyardRTA': "Woods Hole, Martha's Vineyard and Nantucket Steamship Authority",
    'CapeCodRTA': "Cape Cod Regional Transit Authority",
    'LowellRTA': 'Lowell Regional Transit Authority',
    'CapeAnnRTA': "Cape Ann Transportation Authority",
    'BerkshireRTA': "Berkshire Regional Transit Authority",
    'MontachusettRTA': "Montachusett Regional Transit Authority",
    'MerrimackValleyRTA': "Merrimack Valley Regional Transit Authority",
    'PioneerValleyRTA': 'Pioneer Valley Transit Authority',
    'MetroWestRTA': 'MetroWest Regional Transit Authority',
    'WRTA': 'Worcester Regional Transit Authority',
    'BrocktonAreaRTA': 'Brockton Area Transit Authority',
    'SoutheasternRTA': 'Southeastern Regional Transit Authority'
}


def get_bus_stop_data(regenerate) -> pd.DataFrame:
    """Get MA Bus Stop Geometry JSON"""
    RTA_STOPS_URL = 'https://gis.massdot.state.ma.us/arcgis/rest/services/Multimodal/RTAs/FeatureServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json'
    RTA_STOPS_DATA = requests.get(RTA_STOPS_URL)
    stops_data = json.loads(RTA_STOPS_DATA.content)['features']
    return bus_stops_median_household_income(stops_data, regenerate)


def get_route_data() -> pd.DataFrame:
    """Get Bus Route Geometry CSV for RTA's"""
    RTA_ROUTE_URL = 'https://opendata.arcgis.com/datasets/1cb5c63d6f114f8a94c6d5a0e03ae62e_0.csv?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D'
    RTA_ROUTE_DATA = requests.get(RTA_ROUTE_URL)
    return pd.read_csv(StringIO(RTA_ROUTE_DATA.content.decode())).drop(
        columns=[
            'route_type', 'route_desc', 'route_color', 'route_text_color', 
            'route_sort_order', 'min_headway_minutes', 'eligibility_restricted', 
            'continuous_pickup', 'continuous_drop_off', 'route_type_text'
        ]
    )


def get_ridership_data(regenerate=False) -> pd.DataFrame:
    """Get RTA Ridership XLSX"""
    if not regenerate and os.path.exists('data/rta_bus_ridership_ma.csv'):
        return pd.read_csv('data/rta_bus_ridership_ma.csv')
    RTA_RIDERSHIP_URL = 'https://www.transit.dot.gov/sites/fta.dot.gov/files/2020-10/August%202020%20Adjusted%20Database.xlsx'
    RTA_RIDERSHIP_DATA = requests.get(RTA_RIDERSHIP_URL)
    ridership_df = pd.read_excel(BytesIO(RTA_RIDERSHIP_DATA.content), sheet_name='MASTER')
    ridership_df = ridership_df[ridership_df.Mode == 'MB'] # only buses
    ridership_df = ridership_df[ridership_df['HQ State'] == 'MA'][
        [
            '5 digit NTD ID', 'Agency', 'Service Area Population', 'TOS', 
            'Active', 'Passenger Miles FY', 'Unlinked Passenger Trips FY', 
            'Fares FY', 'Operating Expenses FY', 'Average Cost per Trip FY', 
            'Average Fares per Trip FY'
        ]
    ] # only in MA
    return ridership_df.loc[ridership_df['Agency'] != 'Massachusetts Bay Transportation Authority']


def get_tract_population_data(regenerate=False) -> pd.DataFrame:
    """Get population data per census tracts"""
    if not regenerate and os.path.exists('data/tract_population.csv'):
        return pd.read_csv('data/tract_population.csv')
    return get_population().drop(columns=['state', 'county'])


def get_county_population_data(regenerate=False) -> pd.DataFrame:
    """Get population data per county tract"""
    if not regenerate and os.path.exists('data/county_population.csv'):
        return pd.read_csv('data/county_population.csv')

    population_data = np.array(requests.get(
        "https://api.census.gov/data/2018/pep/population?get=COUNTY,DATE_CODE,DATE_DESC,DENSITY,POP,GEONAME,STATE&for=county:*&in=state:25"
    ).json())
    population_headers = population_data[0].tolist()
    population_data =  population_data[1:]
    county_population_df = pd.DataFrame(
        {header: population_data[:, population_headers.index(header)] for header in population_headers}
    ).drop(columns=['state', 'county'])
    return county_population_df.loc[county_population_df['DATE_DESC'] == '7/1/2018 population estimate']


def map_stops_to_routes(regenerate=False):
    """
    Add stops to routes
    
    Assigns each bus stop to a route by calculating the
    distance between each route to bus stop pair, and assigning
    a bus stop to its geometrically closest bus route.
    """
    if not regenerate and os.path.exists('data/bus_stop_route_mapping.csv'):
        return pd.read_csv('data/bus_stop_route_mapping.csv')

    # URLs
    BUS_ROUTES_URL = "https://opendata.arcgis.com/datasets/1cb5c63d6f114f8a94c6d5a0e03ae62e_0.zip"
    BUS_STOPS_URL = "https://opendata.arcgis.com/datasets/9f0b255b1a314b70a396d93d4425f531_1.zip" 
    BUS_ROUTES_DATA = requests.get(BUS_ROUTES_URL)
    BUS_STOPS_DATA = requests.get(BUS_STOPS_URL)
    BUS_ROUTES_ZIP = zipfile.ZipFile(BytesIO(BUS_ROUTES_DATA.content))  
    BUS_STOPS_ZIP = zipfile.ZipFile(BytesIO(BUS_STOPS_DATA.content)) 

    # extract to folder
    BUS_ROUTES_ZIP.extractall(path='data/RTA_Bus_Routes-shp')
    BUS_STOPS_ZIP.extractall(path='data/RTA_Bus_Stops-shp/')
    
    # Filepath
    bus_routes_fp = "data/RTA_Bus_Routes-shp/RTA_Bus_Routes.shp" 
    bus_stops_fp = "data/RTA_Bus_Stops-shp/RTA_Bus_Stops.shp"

    # Read the data
    bus_routes_df = gpd.read_file(bus_routes_fp)
    bus_stops_df = gpd.read_file(bus_stops_fp)

    # Pick specific columns
    routes = bus_routes_df[['OBJECTID','geometry','route_id', 'route_shor', 'route_long']].rename(
        columns={"route_shor": "route_short_name", "route_long": "route_long_name"}
    )
    stops = bus_stops_df[['OBJECTID','geometry','stop_id']]

    # map bus stops to routes
    print(f"Joining bus stops onto routes. This may take a while!")
    now = time.time()

    def get_closest_route_id(stop):
        # Index of geometry field in pandas table

        route_distances_matrix = routes.geometry.apply(lambda line: stop.distance(line))
        closest_route_index = np.argmin(route_distances_matrix)
        return routes.iloc[closest_route_index].route_id

    stops['route_id'] = stops.geometry.apply(get_closest_route_id)
    stops.to_csv('data/bus_stop_route_mapping.csv', index=False)

    return stops 


def get_joined_data(regenerate=False):
    """Returns bus stop area household income data attached with bus routes
    
    Assumes rta_bus_stop_income_ma.csv already exists (aka variable bus_stop_income_df)
    """
    if not regenerate and os.path.exists('data/result.csv'):
        return pd.read_csv('data/result.csv')

    income = pd.read_csv('data/rta_bus_stop_income_ma.csv', index_col=0)

    # get back route names
    routes = pd.read_csv('data/rta_bus_route_ma.csv', index_col=0, usecols=["route_id" ,"route_short_name", "route_long_name"])
    stop_route_map = map_stops_to_routes(regenerate)
    stop_route_map = pd.merge(routes, stop_route_map, on='route_id', how='inner')

    # merge income and routes
    result = pd.merge(income, stop_route_map, on='stop_id', how='inner', suffixes=('','_y'))
    result = result.rename(columns={"OBJECTID_x": "OBJECTID", "geometry_x": "geometry"})

    # remove duplicate columns and rows
    result.drop(result.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)
    result = result.drop_duplicates(subset=['stop_id'])

    return result


def generate(regenerate=False):
    """
    Generates all datasets concurrently
    
    @param regenerate: boolean indicating whether you should regenerate all data or read locally
    """
    now = time.time()
    if not os.path.exists('data'):
        os.makedirs('data')

    routes_df = get_route_data()
    
    tract_population_df = get_tract_population_data(regenerate)
    ridership_df = get_ridership_data(regenerate)
    county_population_df = get_county_population_data(regenerate)

    # join population_df to bus_area_income_df
    bus_stop_income_df = pd.merge(get_bus_stop_data(regenerate), tract_population_df, how='inner', left_on='census_tract', right_on='tract')

    # drop negative median household values data
    bus_stop_income_df['median_household_income'] = bus_stop_income_df['median_household_income'].astype(float)
    bus_stop_income_df = bus_stop_income_df[bus_stop_income_df.median_household_income > 0] 
    bus_stop_income_df.dropna()

    # rename population column
    bus_stop_income_df = bus_stop_income_df.rename(columns={"B01003_001E": "population"})

    # drop duplicate bus stops
    bus_stop_income_df = bus_stop_income_df.drop_duplicates(subset=['stop_id'])

    # drop unnecessary columns and rows
    bus_stop_income_df = bus_stop_income_df.drop(columns=['tract', 'stop_code', 'location_type', 'parent_station', 'wheelchair_boarding', 'platform_code', 'zone_id', 'stop_timezone', 'position', 'direction', 'state', 'stop_desc'])

    bus_stop_income_df.to_csv('data/rta_bus_stop_income_ma.csv', index=False)
    routes_df.to_csv('data/rta_bus_route_ma.csv', index=False)
    ridership_df.to_csv('data/rta_bus_ridership_ma.csv', index=False)
    county_population_df.to_csv('data/county_population.csv', index=False)
    tract_population_df.to_csv('data/tract_population.csv', index=False)

    result = get_joined_data(regenerate)
    result.to_csv('data/result.csv', index=False)

    print(f"Finished all dataset gathering and preprocessing in {time.time() - now}s")
    return {
        "routes_df": routes_df,
        "ridership_df": ridership_df,
        "tract_population_df": tract_population_df,
        "county_population_df": county_population_df,
        "bus_stop_income": bus_stop_income_df,
        "result": result
    }
