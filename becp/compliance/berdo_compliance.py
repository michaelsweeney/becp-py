def get_berdo_compliance():
    return True


non_electric_emissions_factors = {
    'gas': 53.11,
    'fuel_1': 73.5,
    'fuel_2': 74.21,
    'fuel_4': 75.29,
    'diesel': 74.21,
    'district_steam': 66.4,
    'district_hot_water': 66.4,
    'elec_driven_chiller': 52.7,
    'absorption_chiller_gas': 73.89,
    'engine_driven_chiller_gas': 49.31,
}

# kg CO2e/ MMBtu
electric_emissions_factors_by_year = {
    2021: 81,
    2022: 79,
    2023: 77,
    2024: 75,
    2025: 73,
    2026: 71,
    2027: 69,
    2028: 67,
    2029: 65,
    2030: 62,
    2031: 60,
    2032: 58,
    2033: 56,
    2034: 54,
    2035: 52,
    2036: 50,
    2037: 48,
    2038: 46,
    2039: 44,
    2040: 42,
    2041: 40,
    2042: 37,
    2043: 35,
    2044: 33,
    2045: 31,
    2046: 29,
    2047: 27,
    2048: 25,
    2049: 23,
    2050: 21,
    2051: 21,
}


'''
    arrays correspond to the following years:
    2025-2029
    2030-2034
    2035-2039
    2040-2044
    2045-2049
    2050-
    units are kgCO2e/SF
'''
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

'''
unit conversions (from js)
const elec_kwh_to_mmbtu = (kwh) => kwh * 0.003412;
const gas_therms_to_mmbtu = (therms) => therms * 0.1;
const fuel_one_gallons_to_mmbtu = (gal) => gal * 0.141;
const fuel_two_gallons_to_mmbtu = (gal) => gal * 0.1467;
const fuel_four_gallons_to_mmbtu = (gal) => gal * 0.51;
const diesel_gallons_to_mmbtu = (gal) => gal * 0.137381;

// mmbtu to native
const elec_mmbtu_to_kwh = (mmbtu) => Math.round(mmbtu / 0.003412);
const gas_mmbtu_to_therms = (mmbtu) => Math.round(mmbtu / 0.1);
const fuel_one_mmbtu_to_gallons = (mmbtu) => Math.round(mmbtu / 0.141);
const fuel_two_mmbtu_to_gallons = (mmbtu) => Math.round(mmbtu / 0.1467);
const fuel_four_mmbtu_to_gallons = (mmbtu) => Math.round(mmbtu / 0.51);
const diesel_mmbtu_to_gallons = (mmbtu) => Math.round(mmbtu / 0.137381);
'''
