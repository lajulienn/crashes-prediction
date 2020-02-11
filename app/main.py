from datetime import datetime

from flask import Flask, render_template, jsonify, request

from .crash_predictor import CrashPredictor
from .feature_constructor import FeatureConstructor

app = Flask(__name__)
featureConstructor = None
crashPredictor = None


def init():
    global featureConstructor, crashPredictor
    featureConstructor = FeatureConstructor()
    crashPredictor = CrashPredictor()


@app.route("/predict_one_form")
def predict_one():
    return render_template('one_point_predict.html')


@app.route("/predict_one", methods=['GET', 'POST'])
def predict():
    global featureConstructor, crashPredictor
    if featureConstructor is None or crashPredictor is None:
        init()

    date = request.form['date']
    time = request.form['time']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])

    date_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

    features_list = featureConstructor.get_features_list(latitude, longitude, date_time)
    res = {
        'features': features_list,
        'crash_probability': crashPredictor.predict(features_list)
    }

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
