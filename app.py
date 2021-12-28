from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from becp import projections
app = Flask(__name__)
CORS(app)


@app.route('/get_projection_from_reference_buildings/')
def get_projection_from_reference_buildings():
    params = json.loads(request.args.to_dict()['params'])
    projection = projections.get_projection_from_reference_buildings(
        params, as_dict=True)
    return json.dumps(projection)


@app.route('/')
def index():
    return json.dumps({'hey!': 'this is the AKF BECP Flask API'})


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
