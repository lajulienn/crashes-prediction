import os
from datetime import datetime
from random import random
from timeit import default_timer as timer

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from tqdm import tqdm
import geojson
from geojson import Feature, Point, FeatureCollection

from crash_predictor import CrashPredictor
from feature_constructor import FeatureConstructor
from path_builder import get_path_points_between_coordinates

app = Flask(__name__)
CORS(app)

featureConstructor = None
crashPredictor = None


def init():
    global featureConstructor, crashPredictor
    featureConstructor = FeatureConstructor()
    crashPredictor = CrashPredictor()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')



@app.route("/predict_one_form")
def predict_one_form():
    return render_template('one_point_predict.html')


@app.route("/predict_form")
def predict_form():
    return render_template('predict.html', current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))


@app.route("/predict_one", methods=['GET', 'POST'])
def predict_one():
    global featureConstructor, crashPredictor
    if featureConstructor is None or crashPredictor is None:
        start = timer()
        init()
        print(f'init(): {timer() - start}')

    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    date_time = datetime.strptime(request.form['time'], '%Y-%m-%d %H:%M')

    features_list = featureConstructor.get_features_list(latitude, longitude, date_time)
    start = timer()
    probability = crashPredictor.predict(features_list)
    print(f'predict(): {timer() - start}')

    result = {
        'features': features_list,
        'crash_probability': probability,
    }

    return jsonify(result)



@app.route("/predict", methods=['GET', 'POST'])
def predict():
    global featureConstructor, crashPredictor
    if featureConstructor is None or crashPredictor is None:
        init()

    origin = request.form['origin'].split(', ')
    destination = request.form['destination'].split(', ')
    time = request.form['time']
    date_time = datetime.strptime(time, '%Y-%m-%d %H:%M')

    path_points = get_path_points_between_coordinates(origin, destination)

    result = []

    for point in tqdm(path_points):
        longitude = point[0]
        latitude = point[1]
        features_list = featureConstructor.get_features_list(latitude, longitude, date_time)
        probability = crashPredictor.predict(features_list)
        result.append({
            'latitude': latitude,
            'longitude': longitude,
            'probability': probability,
        })

    return jsonify(result)


@app.route("/test", methods=['GET', 'POST'])
def test():
    origin = request.form['origin'].split(', ')
    destination = request.form['destination'].split(', ')
    time = request.form['time']
    date_time = datetime.strptime(time, '%Y-%m-%d %H:%M')

    fc = FeatureCollection(list(map(lambda t: Feature(geometry=Point(t), properties={'probability': random()}),
                get_path_points_between_coordinates(origin, destination))))

    return geojson.dumps(fc)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
