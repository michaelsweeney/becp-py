
import pandas as pd
import numpy as np

from pathlib import Path

path = Path(__file__).parent.resolve()

ENDUSE_FILE = str(path) + '/data/reference_buildings_enduses.csv'
SUMMARY_FILE = str(path) + '/data/reference_buildings_summary.csv'


def get_reference_building_heating_coil_loads(
    climate_zone, ashrae_standard, building_type
):
    summaries = pd.read_csv(SUMMARY_FILE)
    query = f'climate_zone == "{climate_zone}" & building_type == "{building_type}" & ashrae_standard == "{ashrae_standard}"'
    simfile = summaries.query(query)

    return float(simfile['annual_coil_heating_kbtu'].values[0])


def get_reference_building_cooling_coil_loads(
    climate_zone, ashrae_standard, building_type
):
    summaries = pd.read_csv(SUMMARY_FILE)
    query = f'climate_zone == "{climate_zone}" & building_type == "{building_type}" & ashrae_standard == "{ashrae_standard}"'
    simfile = summaries.query(query)

    return float(simfile['annual_coil_cooling_kbtu'].values[0])


def get_reference_building(
        building_type,
        climate_zone,
        ashrae_standard
):
    enduses = pd.read_csv(ENDUSE_FILE)
    summaries = pd.read_csv(SUMMARY_FILE)

    query = f'climate_zone == "{climate_zone}" & building_type == "{building_type}" & ashrae_standard == "{ashrae_standard}"'

    query_result_df = summaries.query(query)

    sim_name = query_result_df['sim_name'].values[0]

    query_enduses = enduses.query(f'sim_name == "{sim_name}"')

    query_enduses = query_enduses[[
        'sim_name',
        'enduse',
        'subcategory',
        'fuel',
        'absolute_kbtu',
        'kbtu_per_sf_total',
        'kbtu_per_sf_conditioned'
    ]].reset_index(drop=True).set_index(['enduse', 'subcategory', 'fuel'])

    return query_enduses
