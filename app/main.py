import importlib
from datetime import datetime

from flask import Flask, render_template, jsonify

from . import config
from .crash_predictor import CrashPredictor
from .feature_constructor import FeatureConstructor
from .weather_forecast import forecast

# import module from code
spec = importlib.util.spec_from_file_location("getncepreanalisys", config.WEATHER_PATH + '/getncepreanalisys.py')
getncepreanalisys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(getncepreanalisys)


app = Flask(__name__)
featureConstructor = FeatureConstructor()
crashPredictor = CrashPredictor()

@app.route("/")
def hello():
    return render_template('main.html')

@app.route("/predict", methods=['GET'])
def predict():
    # date = request.form['date']
    # time = request.form['time']
    # origin = request.form['origin']
    # destination = request.form['destination']
    # date_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

    date_time = datetime.now()
    origin = [44.314566, 38.701589]
    destination = ['44.344929', '38.706081']

    global featureConstructor
    features_list = featureConstructor.get_features_list(origin[0], origin[1], date_time)
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