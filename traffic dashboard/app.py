
from flask import Flask, render_template, jsonify
from traffic_state import get_traffic

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/api/traffic")
def traffic_api():
    return jsonify(get_traffic())

if __name__ == "__main__":
    app.run(debug=True)
