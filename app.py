from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
import json
from becp import projections
from becp.compliance import ll97_compliance, berdo_compliance
app = Flask(__name__)
CORS(app)


@app.route('/')
def site_map():
    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))

    docstrings = []
    for url, endpoint in links:
        try:
            func = getattr(projections, endpoint)
            docstrings.append((url, func.__doc__))
        except:
            pass

    docstrings_text = []
    for endpoint, doc in docstrings:
        docstrings_text.append(
            '<b>' + endpoint + '</b>' + ': <br>' +
            '<i>' + doc.replace('\n', '<br>').strip() + '</i>'
            + '<br><br>'
        )

    return f'''
        <div>
            <h2>akf becp flask api</h2>
            <h3>site map</h3>
            {''.join([f'<div>{x}</div>' for x in links])}
            <h3>docstrings</h3>   
            {''.join([f'<div>{x}</div>' for x in docstrings_text])}

        </div>
        '''


@ app.route('/get_projection_from_reference_buildings/')
def get_projection_from_reference_buildings():
    params = json.loads(request.args.to_dict()['params'])
    projection = projections.get_projection_from_reference_buildings(
        params,
        as_json=True
    )

    projection = json.dumps(projection)
    return projection


@ app.route('/get_projection_from_manual_enduses/')
def get_projection_from_manual_enduses():
    params = json.loads(request.args.to_dict()['params'])
    projection = projections.get_projection_from_manual_enduses(
        params,
        as_json=True
    )
    projection = json.dumps(projection)
    return projection


@ app.route('/get_all_climate_zones/')
def get_all_climate_zones():
    res = projections.get_all_climate_zones()
    res = json.dumps(res.tolist())
    return res


@ app.route('/get_all_ashrae_standards/')
def get_all_ashrae_standards():
    res = projections.get_all_ashrae_standards()
    res = json.dumps(res.tolist())
    return res


@ app.route('/get_all_building_types/')
def get_all_building_types():
    res = projections.get_all_building_types()
    res = json.dumps(res.tolist())
    return res


@ app.route('/get_all_cambium_cases/')
def get_all_cambium_cases():
    res = projections.get_all_cambium_cases()
    res = json.dumps(res.tolist())
    return res


@ app.route('/get_all_states/')
def get_all_states():
    res = projections.get_all_states()
    res = json.dumps(res.tolist())
    return res


@ app.route('/get_all_reference_buildings_data/')
def get_reference_buildings_data():
    res = projections.get_reference_buildings_data(as_json=True)
    return json.dumps(res)


@ app.route('/get_all_cambium_projections_data/')
def get_cambium_projections_data():
    res = projections.get_cambium_projections_data(as_json=True)
    return json.dumps(res)


@ app.route('/compliance/compile_ll97_summary/')
def compile_ll97_summary():
    params = json.loads(request.args.to_dict()['params'])
    res = ll97_compliance.compile_ll97_summary(params)
    return json.dumps(res)


@ app.route('/compliance/compile_berdo_summary/')
def compile_berdo_summary():
    params = json.loads(request.args.to_dict()['params'])
    res = berdo_compliance.compile_berdo_summary(params)
    return json.dumps(res)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
