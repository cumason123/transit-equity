import geopandas as gpd
import pandas as pd
import requests
import os, zipfile
import io


def add_census_tract(dataframe):
    if not os.path.exists('data/tl_2019_25_tract.shp'):
        r = requests.get('https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_25_tract.zip')
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("./data")

    polygons = gpd.read_file("data/tl_2019_25_tract.shp")
    polygons = polygons.rename(columns={"TRACTCE": "census_tract"}, index=str)
    polygons = polygons.to_crs("EPSG:4326")
    gdf = dataframe
    df = gpd.sjoin(gdf, polygons[['census_tract', 'geometry']], how='left', op='within')
    df.drop(columns=['index_right'], inplace=True)
    return df


def get_median_hh_income():
    '''
    Returns Pandas DataFrame representation Median Household Income Estimate by Census Tract for MA.
    American Community Survey (ACS) 2018 Census data used.
    Specific table: ACS 2018 5-year detailed table "B19013_001E"
    '''
    URL = "https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:*&in=state:25"

    response = requests.get(url = URL)
    data = response.json()

    median_income_df = pd.DataFrame(data[1:len(data)-1], columns = data[0])

    return median_income_df


def bus_stops_median_household_income(stops_data):
    '''
    Adds household median income to stops data
    '''
    if os.path.exists('data/bus_area_income.csv'):
        return pd.read_csv('data/bus_area_income.csv')
    
    try:
        stops_data_parsed = []
        for stop in stops_data:
            stop_reformatted = {}
            stop_reformatted['geometry'] = stop['geometry']
            for key in stop['attributes']:
                stop_reformatted[key] = stop['attributes'][key]
            stops_data_parsed.append(stop_reformatted)
        gdf = gpd.GeoDataFrame(stops_data_parsed)
        df = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(
            [stop['geometry']['x'] for stop in stops_data], 
            [stop['geometry']['y'] for stop in stops_data], crs='EPSG:4326')
        )
        census_df = add_census_tract(df)
        census_df = census_df.join(
            get_median_hh_income().set_index('tract'), 
            on='census_tract'
        ).rename(columns={'B19013_001E': 'median_household_income'})
        census_df.to_csv('data/bus_area_income.csv', index=False)
        return census_df
    except:
        raise Exception('You probably need to install rtree or have local file ../data/bus_area_income.csv!')


def get_population():
    '''
    Returns Pandas DataFrame representation Unweighted Sample Count of the Population by Census Tract for MA.
    American Community Survey (ACS) 2018 Census data used.
    Specific table: ACS 2018 5-year detailed table "B00001_001E"
    '''
    URL = "https://api.census.gov/data/2018/acs/acs5?get=B00001_001E&for=tract:*&in=state:25"
    response = requests.get(url = URL)
    data = response.json()

    population_df = pd.DataFrame(data[1:len(data)-1], columns = data[0])

    return population_df
