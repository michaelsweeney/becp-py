from flask import Flask, request, jsonify
import json
from becp import projections
app = Flask(__name__)


@app.route('/get_projection_from_reference_buildings/', methods=['GET'])
def respond():
    params = json.loads(request.data)

    projection = projections.get_projection_from_reference_buildings(
        params, as_dict=True)

    return json.dumps(projection)


@app.route('/')
def index():
    return f"<h2>{'welcome to Python BECP (Buiding Energy and Carbon Projection)'}</h2>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
