from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('main.html')

@app.route("/predict", methods=['POST'])
def predict():
    origin = request.form['origin']
    destination = request.form['destination']
    date = request.form['date']
    time = request.form['time']

    return jsonify(success=True)


if __name__ == "__main__":
    app.run()