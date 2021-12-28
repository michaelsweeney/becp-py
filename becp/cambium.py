

import pandas as pd
import numpy as np
from pathlib import Path

path = Path(__file__).parent.resolve()
CAMBIUM_FILE = str(path) + '/data/cambium_projections.csv'


# kg_per_kbtu
non_electric_emissions_factors = {
    'Natural Gas': 0.05311,
}
# for reference
berdo_emissions_factors_by_year = {
    2021: 0.081 * 3412,
    2022: 0.079 * 3412,
    2023: 0.077 * 3412,
    2024: 0.075 * 3412,
    2025: 0.073 * 3412,
    2026: 0.071 * 3412,
    2027: 0.069 * 3412,
    2028: 0.067 * 3412,
    2029: 0.065 * 3412,
    2030: 0.062 * 3412,
    2031: 0.060 * 3412,
    2032: 0.058 * 3412,
    2033: 0.056 * 3412,
    2034: 0.054 * 3412,
    2035: 0.052 * 3412,
    2036: 0.050 * 3412,
    2037: 0.048 * 3412,
    2038: 0.046 * 3412,
    2039: 0.044 * 3412,
    2040: 0.042 * 3412,
    2041: 0.040 * 3412,
    2042: 0.037 * 3412,
    2043: 0.035 * 3412,
    2044: 0.033 * 3412,
    2045: 0.031 * 3412,
    2046: 0.029 * 3412,
    2047: 0.027 * 3412,
    2048: 0.025 * 3412,
    2049: 0.023 * 3412,
    2050: 0.021 * 3412,
    2051: 0.021 * 3412,
}


def get_cambium_projection(state, case):

    if case == "BERDO":
        projection = pd.DataFrame(berdo_emissions_factors_by_year.items())
        projection.columns = 'year', 'co2_gen_kg_per_mwh'
        projection['co2_load_enduse_kg_per_mwh'] = projection['co2_gen_kg_per_mwh']
        projection['state'] = 'MA'
        projection['case'] = 'BERDO'

    else:
        cambium = pd.read_csv(CAMBIUM_FILE)
        query = f'state == "{state}" & case == "{case}"'
        projection = cambium.query(query)

        projection = projection[[
            'state',
            'case',
            'year',
            'co2_gen_kg_per_mwh',
            'co2_load_enduse_kg_per_mwh'
        ]].reset_index(drop=True)

    if len(projection.index) < 1:
        raise ValueError(
            'error finding projection case. Ensure a valid projection case has been used.')

    return projection


def get_carbon_projections(enduses, area, projection_factors, projection_metric='co2_gen_kg_per_mwh'):

    enduses = enduses.reset_index()
    elec_factor_dict = projection_factors.set_index(
        'year')[projection_metric].to_dict()

    # projection_years = [2020, 2022, 2024, 2026, 2028, 2030,
    #                     2032, 2034, 2036, 2038, 2040, 2042, 2044,
    #                     2046, 2048, 2050]

    projection_years = list(elec_factor_dict.keys())

    emissions_dict = []

    for year in projection_years:
        elec_kg_per_mwh = elec_factor_dict[year]
        elec_kg_per_kbtu = elec_kg_per_mwh / 3412

        emissions_factors = non_electric_emissions_factors.copy()
        emissions_factors['Electricity'] = elec_kg_per_kbtu

        def get_kg_co2(x):
            factor = emissions_factors[x['fuel']]

            return factor * x['kbtu_absolute']

        emissions_df = enduses.copy()
        emissions_df['kg_co2'] = emissions_df.apply(get_kg_co2, axis=1)

        kg_co2_absolute = emissions_df['kg_co2'].sum()
        kg_co2_per_sf = kg_co2_absolute / area

        emissions_dict.append({
            'year': year,
            'elec_kg_per_kbtu': elec_kg_per_kbtu,
            'kg_co2_absolute': kg_co2_absolute,
            'kg_co2_per_sf': kg_co2_per_sf
        })

    projection_df = pd.DataFrame.from_dict(emissions_dict)

    return projection_df
