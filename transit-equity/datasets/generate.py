import requests
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import json
import os
from lib import *


def get_bus_stop_data() -> pd.DataFrame:
    """Get MA data for RTA bus stops"""
    RTA_STOPS_URL = 'https://gis.massdot.state.ma.us/arcgis/rest/services/Multimodal/RTAs/FeatureServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json'
    RTA_STOPS_DATA = requests.get(RTA_STOPS_URL)
    stops_data = json.loads(RTA_STOPS_DATA.content)['features']
    return bus_stops_median_household_income(stops_data)


def get_route_data() -> pd.DataFrame:
    """Get route data for RTA's"""
    RTA_ROUTE_URL = 'https://opendata.arcgis.com/datasets/1cb5c63d6f114f8a94c6d5a0e03ae62e_0.csv?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D'
    RTA_ROUTE_DATA = requests.get(RTA_ROUTE_URL)
    return pd.read_csv(StringIO(RTA_ROUTE_DATA.content.decode()))


def get_ridership_data() -> pd.DataFrame:
    """Get ridership data for RTA's"""
    RTA_RIDERSHIP_URL = 'https://www.transit.dot.gov/sites/fta.dot.gov/files/2020-10/August%202020%20Adjusted%20Database.xlsx'
    RTA_RIDERSHIP_DATA = requests.get(RTA_RIDERSHIP_URL)
    ridership_df = pd.read_excel(BytesIO(RTA_RIDERSHIP_DATA.content), sheet_name='MASTER')
    ridership_df = ridership_df[ridership_df.Mode == 'MB'] # only buses
    return ridership_df[ridership_df['HQ State'] == 'MA'] # only buses


def get_tract_population_data() -> pd.DataFrame:
    """Get population"""
    return get_population().drop(columns=['state', 'county'])


def get_county_population_data() -> pd.DataFrame:
    """"""
    population_data = np.array(requests.get(
        "https://api.census.gov/data/2018/pep/population?get=COUNTY,DATE_CODE,DATE_DESC,DENSITY,POP,GEONAME,STATE&for=county:*&in=state:25"
    ).json())
    population_headers = population_data[0].tolist()
    population_data =  population_data[1:]
    county_population_df = pd.DataFrame(
        {header: population_data[:, population_headers.index(header)] for header in population_headers}
    ).drop(columns=['state', 'county'])
    return county_population_df.loc[county_population_df['DATE_DESC'] == '7/1/2018 population estimate']


def join_stop_route_data():


def generate():
    if not os.path.exists('../data'):
        raise Exception('Missing ../data/bus_area_income.csv xor ../data/tl_2019_25_tract.shp')

    route_df = 
    bus_area_income_df = get_bus_stop_data()
    population_df = get_tract_population_data()
    # join population_df to bus_area_income_df
    bus_area_income_df = pd.merge(bus_area_income_df, population_df, how='inner', left_on='census_tract', right_on='tract')