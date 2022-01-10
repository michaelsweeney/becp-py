
buildingtypes = {
    'A': 'A (Assembly)',
    'B_norm': 'B (Business)',
    'B_health': 'B (Healthcare)',
    'E': 'E (Educational)',
    'F': 'F (Factory/Industrial)',
    'H': 'H (High Hazard)',
    'I1': 'I-1 (Institutional)',
    'I2': 'I-2 (Institutional)',
    'I3': 'I-3 (Institutional)',
    'I4': 'I-4 (Institutional)',
    'M': 'M (Mercantile)',
    'R1': 'R-1 (Residential)',
    'R2': 'R-2 (Residential)',
    'S': 'S (Storage)',
    'U': 'U (Utility/Misc)',
}

# 2024-2029, 2030-2034, 2035-2050
co2limitsbybuildingtype = {
    'A': [0.01074, 0.0042, 0.0014],
    'B_health': [0.02381, 0.0133, 0.0014],
    'B_norm': [0.00846, 0.00453, 0.0014],
    'E': [0.00758, 0.00344, 0.0014],
    'F': [0.00574, 0.00167, 0.0014],
    'H': [0.02381, 0.0133, 0.0014],
    'I1': [0.01138, 0.00598, 0.0014],
    'I2': [0.02381, 0.0133, 0.0014],
    'I3': [0.02381, 0.0133, 0.0014],
    'I4': [0.00758, 0.00344, 0.0014],
    'M': [0.01181, 0.00403, 0.0014],
    'R1': [0.00987, 0.00526, 0.0014],
    'R2': [0.00675, 0.00407, 0.0014],
    'S': [0.00426, 0.0011, 0.0014],
    'U': [0.00426, 0.0011, 0.0014]
}


# kbtu-to-tons carbon
kbtu_to_carbon_conversions = {
    'electricity': 0.000084689,
    'natural_gas': 0.00005311,
    'steam': 0.00004493,
    'fuel_two': 0.00007421,
    'fuel_four': 0.00007529,
}

fine_per_ton_co2 = 268


def get_emissions_thresholds(building):
    '''
    returns whole-building emissions thresholds 
    array of three values: 2024-2029 threshold,
    2025-2029 
    '''
    types = building['types']
    whole_building_emissions_thresholds = [0, 0, 0]
    for t in types:
        area = t['area']
        building_type = t['type']
        type_thresholds = co2limitsbybuildingtype[building_type]
        type_thresholds = [x * area for x in type_thresholds]

        whole_building_emissions_thresholds = [val + type_thresholds[i]
                                               for i, val in enumerate(whole_building_emissions_thresholds)]

    return whole_building_emissions_thresholds


def get_annual_building_carbon(building):
    '''
    utility values in kbtu
    returns total carbon tons
    '''
    utilities = building['utilities']

    annual_carbon = sum([
        u['val'] * kbtu_to_carbon_conversions[u['type']]
        for u in utilities
    ])
    return annual_carbon


def get_carbon_above_thresholds(thresholds, annual_carbon):
    return [annual_carbon - t for t in thresholds]


def get_annual_penalties(carbon_above_thresholds):
    return [max(t, 0) * fine_per_ton_co2 for t in carbon_above_thresholds]


def get_total_building_area(building_inputs):
    return sum([x['area'] for x in building_inputs['types']])


def compile_ll97_summary(building_inputs):
    '''
    building_input sample:

        building_inputs = {
            'types': [
                {'type': 'B_norm', 'area': 50000},
                {'type': 'A', 'area': 3000},
            ],
            'utilities': [
                {'type': 'elec', 'val': 950000 * 3.412},  # kbtu
                {'type': 'gas', 'val': 10000 * 100},  # kbtu
            ]
        }
    '''

    total_area = get_total_building_area(building_inputs)
    if total_area < 25000:
        return {'invalid': 'buildings under 25,000 are unregulated for ll97'}

    emissions_thresholds = get_emissions_thresholds(
        building_inputs)
    annual_building_carbon_tons = get_annual_building_carbon(building_inputs)
    carbon_above_thresholds = get_carbon_above_thresholds(
        emissions_thresholds, annual_building_carbon_tons)
    annual_penalties = get_annual_penalties(carbon_above_thresholds)

    return {
        'emissions_thresholds': emissions_thresholds,
        'annual_building_carbon_tons': annual_building_carbon_tons,
        'carbon_above_thresholds': carbon_above_thresholds,
        'annual_penalties': annual_penalties
    }


if __name__ == "__main__":
    # testing only
    building_inputs_test = {
        'types': [
            {'type': 'B_norm', 'area': 50000},
            {'type': 'A', 'area': 3000},
        ],
        'utilities': [
            {'type': 'electricity', 'val': 950000 * 3.412},  # kbtu
            {'type': 'natural_gas', 'val': 10000 * 100},  # kbtu
        ]
    }

    print(compile_ll97_summary(building_inputs_test))
