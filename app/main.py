import importlib
from datetime import datetime

from flask import Flask, render_template, jsonify, request

from . import config
from .crash_predictor import CrashPredictor
from .feature_constructor import FeatureConstructor
from .weather_forecast import forecast

# import module from code
spec = importlib.util.spec_from_file_location("getncepreanalisys", config.WEATHER_PATH + '/getncepreanalisys.py')
getncepreanalisys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(getncepreanalisys)


app = Flask(__name__)
featureConstructor = None
crashPredictor = None

@app.route("/")
def hello():
    return render_template('main.html')

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    global featureConstructor, crashPredictor
    if featureConstructor is None:
        featureConstructor = FeatureConstructor()
    if crashPredictor is None:
        crashPredictor = CrashPredictor()

    date = request.form['date']
    time = request.form['time']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])

    date_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

    # date_time = datetime.now()
    # origin = [44.314566, 38.701589]
    # destination = ['44.344929', '38.706081']

    features_list = featureConstructor.get_features_list(latitude, longitude, date_time)
    res = {
        'features': features_list,
        'crash_probability': crashPredictor.predict(features_list)
    }

    return jsonify(res)

@app.route("/weather")
def weather():
    res = forecast()
    return jsonify(res)


@app.route("/test")
def test():
    date_time = datetime.now()
    origin = [44.314566, 38.701589]
    destination = ['44.344929', '38.706081']

    features = featureConstructor.get_features_list(origin[0], origin[1], date_time)
    return jsonify(features)


if __name__ == "__main__":
    app.run(host='0.0.0.0')