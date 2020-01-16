from flask import Flask, render_template, request, jsonify
from .feature_constructor import FeatureConstructor
from . import config
from datetime import datetime
import pickle


app = Flask(__name__)

feature_constructor = FeatureConstructor()

@app.route("/")
def hello():
    return render_template('main.html')

@app.route("/predict", methods=['POST'])
def predict():
    origin = request.form['origin']
    destination = request.form['destination']
    date = request.form['date']
    time = request.form['time']

    date_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

    features = feature_constructor.get_feature_dataframe(origin, destination, date_time)

    return jsonify(features)

@app.route("/test")
def test():
    date_time = datetime.now()
    origin = [44.314566, 38.701589]
    destination = ['44.344929', '38.706081']

    features = feature_constructor.get_feature_dataframe(origin[0], origin[1], date_time)
    return jsonify(features)


if __name__ == "__main__":
    app.run(host='0.0.0.0')