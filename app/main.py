from datetime import datetime
from timeit import default_timer as timer

from flask import Flask, render_template, jsonify, request
from tqdm import tqdm

from .crash_predictor import CrashPredictor
from .feature_constructor import FeatureConstructor
from .path_builder import get_path_points_between_coordinates

app = Flask(__name__)
featureConstructor = None
crashPredictor = None


def init():
    global featureConstructor, crashPredictor
    featureConstructor = FeatureConstructor()
    crashPredictor = CrashPredictor()


@app.route("/predict_one_form")
def predict_one_form():
    return render_template('one_point_predict.html')


@app.route("/predict_form")
def predict_form():
    return render_template('predict.html')


@app.route("/predict_one", methods=['GET', 'POST'])
def predict_one():
    global featureConstructor, crashPredictor
    if featureConstructor is None or crashPredictor is None:
        start = timer()
        init()
        print(f'init(): {timer() - start}')

    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    date = request.form['date']
    time = request.form['time']
    date_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

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

    origin = [request.form['origin_latitude'], request.form['origin_longitude']]
    destination = [request.form['destination_latitude'], request.form['destination_longitude']]
    date = request.form['date']
    time = request.form['time']
    date_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

    path_points = get_path_points_between_coordinates(origin, destination)

    result = []

    for point in tqdm(path_points):
        latitude = point[0]
        longitude = point[1]
        features_list = featureConstructor.get_features_list(latitude, longitude, date_time)
        probability = crashPredictor.predict(features_list)
        result.append({
            'latitude': latitude,
            'longitude': longitude,
            'probability': probability,
        })

    return jsonify(result)


@app.route("/test")
def test():
    date_time = datetime.now()
    origin = ['44.623110', '39.108736']
    destination = ['44.701639', '39.230262']

    points = get_path_points_between_coordinates(origin, destination)
    return jsonify(points)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
