
acp_per_ton = 234

acp_per_kg = acp_per_ton * 0.001

non_electric_emissions_factors = {
    'natural_gas': 0.05311,
    'fuel_one': 0.0735,
    'fuel_two': 0.07421,
    'fuel_four': 0.07529,
    'diesel': 0.07421,
    'district_steam': 0.0664,
    'district_hot_water': 0.0664,
    'elec_driven_chiller': 0.0527,
    'absorption_chiller_gas': 0.07389,
    'engine_driven_chiller_gas': 0.04931,
}

# kbtu-to-kg carbon
electric_emissions_factors_by_year = {
    2021: 0.081,
    2022: 0.079,
    2023: 0.077,
    2024: 0.075,
    2025: 0.073,
    2026: 0.071,
    2027: 0.069,
    2028: 0.067,
    2029: 0.065,
    2030: 0.062,
    2031: 0.060,
    2032: 0.058,
    2033: 0.056,
    2034: 0.054,
    2035: 0.052,
    2036: 0.050,
    2037: 0.048,
    2038: 0.046,
    2039: 0.044,
    2040: 0.042,
    2041: 0.040,
    2042: 0.037,
    2043: 0.035,
    2044: 0.033,
    2045: 0.031,
    2046: 0.029,
    2047: 0.027,
    2048: 0.025,
    2049: 0.023,
    2050: 0.021,
    2051: 0.021,
}


threshold_periods = [
    '2025-2029',
    '2030-2034',
    '2035-2039',
    '2040-2044',
    '2045-2049',
    '2050-',
]

# lists correspond to threshold_periods
emissions_standards = {
    'assembly': [7.8, 4.6, 3.3, 2.1, 1.1, 0],
    'college_university': [10.2, 5.3, 3.8, 2.5, 1.2, 0],
    'education': [3.9, 2.4, 1.8, 1.2, 0.6, 0],
    'food_sales_service': [17.4, 10.9, 8.0, 5.4, 2.7, 0],
    'healthcare': [15.4, 10.0, 7.4, 4.9, 2.4, 0],
    'lodging': [5.8, 3.7, 2.7, 1.8, 0.9, 0],
    'manufacturing_industrial': [23.9, 15.3, 10.9, 6.7, 3.2, 0],
    'multifamily_housing': [4.1, 2.4, 1.8, 1.1, 0.6, 0],
    'office': [5.3, 3.2, 2.4, 1.6, 0.8, 0],
    'retail': [7.1, 3.4, 2.4, 1.5, 0.7, 0],
    'services': [7.5, 4.5, 3.3, 2.2, 1.1, 0],
    'storage': [5.4, 2.8, 1.8, 1.0, 0.4, 0],
    'technology_science': [19.2, 11.1, 7.8, 5.1, 2.5, 0],
}


def get_emissions_thresholds(building):
    '''
    returns whole-building emissions thresholds
    array of six periods values: 
            2025-2029
            2030-2034
            2035-2039
            2040-2044
            2045-2049
            2050-
    '''
    types = building['types']
    whole_building_emissions_thresholds = [0, 0, 0, 0, 0, 0]
    for t in types:
        area = t['area']
        building_type = t['type']
        type_thresholds = emissions_standards[building_type]
        type_thresholds = [x * area for x in type_thresholds]

        whole_building_emissions_thresholds = [val + type_thresholds[i]
                                               for i, val in enumerate(whole_building_emissions_thresholds)]

    whole_building_emissions_threshold_object = [
        {'period': threshold_periods[num], 'val': line}
        for num, line in enumerate(whole_building_emissions_thresholds)
    ]

    return whole_building_emissions_threshold_object


def get_annual_building_carbon_array(building):
    '''
    utility values in kbtu
    returns total carbon kg
    '''
    utilities = building['utilities']
    emissions_by_year = []

    for x in range(2021, 2051):
        emission_factors = non_electric_emissions_factors
        emission_factors['electricity'] = electric_emissions_factors_by_year[x]
        annual_carbon = sum([
            u['val'] * emission_factors[u['type']] for u in utilities
        ])
        emissions_by_year.append({'year': x, 'val': annual_carbon})

    return emissions_by_year


def get_threshold_period(year):
    assigned_period = False

    for period in threshold_periods:
        start, end = period.split("-")
        if end == '':
            end = 9999

        if float(start) <= float(year) <= float(end):
            assigned_period = period

    return assigned_period


def get_carbon_above_thresholds(thresholds, annual_carbon):

    carbon_delta = []
    for a in annual_carbon:
        year = a['year']
        val = a['val']
        period = get_threshold_period(year)
        current_threshold = list(
            filter(lambda x: x['period'] == period, thresholds))
        if len(current_threshold) == 0:
            carbon_delta.append({
                'year': year, 'val': 0
            })
        else:
            carbon_delta.append({
                'year': year,
                'val': val - current_threshold[0]['val']
            })

    return carbon_delta


def get_annual_compliance_payments(carbon_above_thresholds):
    return [{
        'year': t['year'],
        'val': max(t['val'], 0) * acp_per_kg
    } for t in carbon_above_thresholds]


def get_total_building_area(building_inputs):
    return sum([x['area'] for x in building_inputs['types']])


def compile_berdo_summary(building_inputs):

    total_area = get_total_building_area(building_inputs)

    emissions_thresholds = get_emissions_thresholds(building_inputs)
    annual_carbon_kg = get_annual_building_carbon_array(building_inputs)

    if total_area < 20000:
        return {'invalid': 'buildings under 25,000 are unregulated for ll97'}
    if total_area < 30000:
        emissions_thresholds = emissions_thresholds[1:]

    carbon_above_thresholds = get_carbon_above_thresholds(
        emissions_thresholds, annual_carbon_kg)

    acp_payments = get_annual_compliance_payments(carbon_above_thresholds)

    emissions_thresholds_per_sf = [x * 1000 /
                                   total_area for x in emissions_thresholds]

    return {
        'acp_payments': acp_payments,
        'carbon_above_thresholds': carbon_above_thresholds,
        'emissions_thresholds': emissions_thresholds,
        'emissions_thresholds_per_sf': emissions_thresholds_per_sf,
        'annual_building_carbon_kg': annual_carbon_kg
    }


if __name__ == "__main__":
    # building_input sample:
    building_inputs = {
        'types': [
            {'type': 'office', 'area': 28000},
        ],
        'utilities': [
            {'type': 'electricity', 'val': 860000 * 3.412},  # kbtu
            {'type': 'natural_gas', 'val': 0 * 100},  # kbtu
        ]
    }

    a = compile_berdo_summary(building_inputs)
