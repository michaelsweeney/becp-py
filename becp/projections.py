
import pandas as pd
import numpy as np

from becp import cambium
from becp import refbuild
import os

from pathlib import Path

path = Path(__file__).parent.resolve()

CAMBIUM_FILE = f'{path}/data/cambium_projections.csv'
ENDUSE_FILE = f'{path}/data/reference_buildings_enduses.csv'
SUMMARY_FILE = f'{path}/data/reference_buildings_summary.csv'


def df_to_json_array(df):
    '''JSONifies dataframes into JS-style array of objects'''
    return list(df.T.to_dict().values())


def get_key(key, d):
    if key in d:
        return d[key]
    else:
        return False


def compile_reference_building_enduses(
    design_areas,
    climate_zone,
    eui_metric='kbtu_per_sf_conditioned'
):
    '''documentation tbd'''

    total_area = 0
    enduse_df_compilation = []

    for d in design_areas:
        colname = eui_metric
        building_type = d['type']
        area = d['area']
        ashrae_standard = d['ashrae_standard']

        heating_fuel = get_key('heating_fuel', d)
        heating_cop = get_key('heating_cop', d)
        dhw_fuel = get_key('dhw_fuel', d)
        dhw_cop = get_key('dhw_cop', d)
        cooling_cop = get_key('cooling_cop', d)

        ref_bldg_enduses = refbuild.get_reference_building(
            climate_zone=climate_zone,
            ashrae_standard=ashrae_standard,
            building_type=building_type,
        )[colname].reset_index()

        ## -- heating efficiency calcs -- ##

        heating_coil_kbtu = refbuild.get_reference_building_heating_coil_loads(
            climate_zone=climate_zone,
            ashrae_standard=ashrae_standard,
            building_type=building_type,
        )

        cooling_coil_kbtu = refbuild.get_reference_building_cooling_coil_loads(
            climate_zone=climate_zone,
            ashrae_standard=ashrae_standard,
            building_type=building_type,
        )

        design_enduses = ref_bldg_enduses.copy()
        renamedict = {}
        abs_colname = 'kbtu_absolute'
        renamedict[eui_metric] = abs_colname
        design_enduses = design_enduses.rename(renamedict, axis=1)

        design_enduses[abs_colname] = design_enduses[abs_colname] * area

        def electrify_gas_heating(x):
            if x['fuel'] == 'Natural Gas' and x['enduse'] == 'Heating':
                # fuel efficiency assumed for reference buildings
                return x[abs_colname] / 0.85
            else:
                return x[abs_colname]

        def electrify_gas_dhw(x):
            if x['fuel'] == 'Natural Gas' and x['enduse'] == 'Water Systems':
                return x[abs_colname] / 0.85
            else:
                return x[abs_colname]

        def apply_dhw_cop(x):
            if x['enduse'] == 'Water Systems':
                return x[abs_colname] / dhw_cop
            else:
                return x[abs_colname]

        def apply_htg_cop(x):
            if x['enduse'] == 'Heating':
                return heating_coil_kbtu / heating_cop
            else:
                return x[abs_colname]

        def apply_clg_cop(x):
            if x['enduse'] == 'Cooling':
                return cooling_coil_kbtu / cooling_cop
            else:
                return x[abs_colname]

        def switch_fuel_type_heating(x):
            if x['enduse'] == 'Heating':
                return heating_fuel
            else:
                return x['fuel']

        def switch_fuel_type_dhw(x):
            if x['enduse'] == 'Water Systems':
                return dhw_fuel
            else:
                return x['fuel']

        if heating_cop:
            design_enduses[abs_colname] = design_enduses.apply(
                electrify_gas_heating, axis=1)
            design_enduses[abs_colname] = design_enduses.apply(
                apply_htg_cop, axis=1)
            design_enduses['fuel'] = design_enduses.apply(
                switch_fuel_type_heating, axis=1)

        if dhw_cop:
            design_enduses[abs_colname] = design_enduses.apply(
                electrify_gas_dhw, axis=1)
            design_enduses[abs_colname] = design_enduses.apply(
                apply_dhw_cop, axis=1)
            design_enduses['fuel'] = design_enduses.apply(
                switch_fuel_type_dhw, axis=1)

        if cooling_cop:
            design_enduses[abs_colname] = design_enduses.apply(
                apply_clg_cop, axis=1)

        ## -- end cooling & heating calcs -- ##

        enduse_df_compilation.append(design_enduses)

        total_area += area

    enduses_absolute_kbtu = pd.concat(
        enduse_df_compilation).fillna(0).groupby(['enduse', 'subcategory', 'fuel']).sum()

    enduses_per_sf = enduses_absolute_kbtu / total_area
    enduses_per_sf = enduses_per_sf.rename(
        {'kbtu_absolute': 'kbtu_per_sf'}, axis=1)

    design_compilation = {
        'enduses_absolute_kbtu': enduses_absolute_kbtu,
        'enduses_per_sf': enduses_per_sf,
        'area': total_area
    }

    return design_compilation


def get_projection_from_reference_buildings(config, as_json=False):
    '''

    if heating_cop, dhw_cop, or cooling_cop is not
    passed under design_areas (or if 'false' is passed
    for any of these), the original reference building
    enduse will be used.


    config schema: 
        argdict = {
            'state': str,
            'climate_zone': str,
            'projection_case': str,
            'design_areas': [
                {
                    'type': str,
                    'area': num,
                    'heating_fuel': str,
                    'dhw_fuel': str,
                    'heating_cop': num,
                    'dhw_cop': num,
                    'cooling_cop': num,
                    'ashrae_standard': str
                },
            ],
        }
    '''
    state = config['state']
    climate_zone = config['climate_zone']
    projection_case = config['projection_case']
    design_areas = config['design_areas']

    projection_factors = cambium.get_cambium_projection(
        state=state,
        case=projection_case
    )

    design_enduses = compile_reference_building_enduses(
        design_areas, climate_zone)

    emissions_projection = cambium.get_carbon_projections(
        enduses=design_enduses['enduses_absolute_kbtu'],
        area=design_enduses['area'],
        projection_factors=projection_factors
    )

    if as_json:
        emissions_projection = df_to_json_array(emissions_projection)
        design_enduses = {k: df_to_json_array(v.reset_index()) if isinstance(
            v, pd.DataFrame) else v for k, v in design_enduses.items()}
        projection_factors = df_to_json_array(projection_factors)

    return {
        'emissions_projection': emissions_projection,
        'enduses': design_enduses,
        'projection_factors': projection_factors
    }


def get_projection_from_manual_enduses(config, as_json=False):
    '''
    config schema: 
    config = {
            state: str,
            projection_case: str
            enduses: [
                {
                    enduse: str,
                    fuel: str,
                    kbtu, num
                }, 
            ]
        }
    '''
    state = config['state']
    projection_case = config['projection_case']

    sim_enduses = pd.DataFrame(config['enduses']).set_index(['enduse', 'fuel'])
    sim_area = config['area']

    design_enduses = {
        'enduses': sim_enduses,
        'enduses_per_sf': sim_enduses / sim_area,
        'area': sim_area
    }

    projection_factors = cambium.get_cambium_projection(
        state=state,
        case=projection_case
    )

    emissions_projection = cambium.get_carbon_projections(
        enduses=design_enduses['enduses'],
        area=design_enduses['area'],
        projection_factors=projection_factors,
        energy_key='kbtu'
    )

    if as_json:
        emissions_projection = df_to_json_array(emissions_projection)
        design_enduses = {k: df_to_json_array(v.reset_index()) if isinstance(
            v, pd.DataFrame) else v for k, v in design_enduses.items()}
        projection_factors = df_to_json_array(projection_factors)

    return {
        'emissions_projection': emissions_projection,
        'enduses': design_enduses,
        'projection_factors': projection_factors
    }


# helpers / general info retrieval

def get_all_climate_zones():
    '''return list of all climate zones in dataset'''
    return pd.read_csv(SUMMARY_FILE).climate_zone.unique()


def get_all_ashrae_standards():
    '''return list of all ashrae standards in dataset'''
    return pd.read_csv(SUMMARY_FILE).ashrae_standard.unique()


def get_all_building_types():
    '''return list of all building types in dataset'''
    return pd.read_csv(SUMMARY_FILE).building_type.unique()


def get_all_cambium_cases():
    '''return list of all cambium cases in dataset'''
    return pd.read_csv(CAMBIUM_FILE).case.unique()


def get_all_states():
    '''return list of all states in dataset'''
    return pd.read_csv(CAMBIUM_FILE).state.unique()


def get_reference_buildings_data(as_json=False):
    '''return object array of all reference building data'''
    enduses = pd.read_csv(ENDUSE_FILE)
    summary = pd.read_csv(SUMMARY_FILE)

    if as_json:
        enduses = df_to_json_array(enduses)
        summary = df_to_json_array(summary)

    return {
        'enduses': enduses,
        'summary': summary
    }


def get_cambium_projections_data(as_json=False):
    '''return object array of all cambium projection data'''
    if as_json:
        return df_to_json_array(pd.read_csv(CAMBIUM_FILE))
    else:
        return pd.read_csv(CAMBIUM_FILE)
